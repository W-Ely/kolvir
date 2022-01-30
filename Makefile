.PHONY=help clean code lint test dev bash deploy ipython kill package lock token \
	serverless

script-directory := scripts
service-directory := kolvir
test-directory := tests
service-files := $(shell find $(service-directory) -name '*.py' -not \( -path '*__pycache__*' \))
test-files := $(shell find $(test-directory) -name '*.py' -not \( -path '*__pycache__*' \))
script-files := $(shell find $(script-directory) -name '*.sh')

ci := $(shell [ -z "$$CI" ] && echo "false" || echo "true")
ifeq ($(ci), false)
context := local
else
context := circle
endif

ifneq (,$(wildcard ./.env))
include .env
endif

all: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## clean dev artifacts
	docker-compose down -v --remove-orphans --rmi all
	docker system prune -f --filter "label=service=kolvir" --volumes
	docker builder prune -a -f
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
	pipenv --clear | true
	pipenv --rm | true
	rm -rf .cache .venv .build .lock .lint .test .dev \
		.coverage serverless pytest_cache dist ipynb_checkpoints .DS_Store \
		kolvir.egg-info

.lock: Makefile Pipfile package.json
	docker build . -t kolvir:base --target base --rm
	docker build . -t kolvir:python-node --target python-node --rm
	# Python
	$(eval container-id := $(shell docker create kolvir:base pipenv lock -v --clear))
	docker container cp Pipfile $(container-id):/app/Pipfile
	docker container start -i $(container-id)
	docker container cp $(container-id):/app/Pipfile.lock Pipfile.lock
	docker rm -v $(container-id)
	chown $(shell id -u):$(shell id -g) Pipfile.lock
	# JavaScript
	$(eval container-id := $(shell docker create kolvir:python-node /bin/bash -c "npm install && npm audit fix --force"))
	docker container cp package.json $(container-id):/app/package.json
	docker container start -i $(container-id)
	docker container cp $(container-id):/app/package-lock.json package-lock.json
	docker rm -v $(container-id)
	chown $(shell id -u):$(shell id -g) package-lock.json
	# consider improving this with audit fix
	@touch .lock

.build: Dockerfile .dockerignore Pipfile Pipfile.lock package.json package-lock.json $(service-files)
	docker build . -t kolvir:base --target base --rm
	docker build . -t kolvir:python-node --target python-node --rm
	docker build . -t kolvir:local --target local --rm
	docker build . -t kolvir:api --target api --rm
	docker build . -t kolvir:circle --target circle --rm
	- docker image prune -f --filter="label=service=kolvir"
	@touch .build

.dev: Makefile Pipfile
	pipenv sync --dev
	@touch .dev

.lint: pyproject.toml .build $(service-files) $(test-files) $(script-files) Makefile
	docker-compose run --rm kolvir.$(context).lint /bin/sh ./scripts/lint.sh \
		$(service-files) $(test-files)
	@touch .lint

t ?= $(test-directory)
.test: pyproject.toml .build $(service-files) $(test-files) $(script-files) Makefile docker-compose.yml Dockerfile
	docker-compose run --rm kolvir.$(context) /bin/sh ./scripts/test.sh $(t) \
		|| (ret=$$?; docker-compose down && exit $$ret)  # This line cleans up and propagates the exit code
	docker-compose down | true
	if [ "$(t)" = "$(test-directory)" ]; then touch .test; fi

lock: .lock  ## Relock depends (uses docker container)

run: .dev .build  ## Run the serverless api locally
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/aws/assume_role.py --role $(deploy-role) --mfa \
		docker-compose run -p 3000-3002:3000-3002 --rm kolvir.$(context) \
			/bin/sh ./scripts/app.sh \
			|| (ret=$$?; docker-compose down && exit $$ret)
	docker-compose down

build: .build  # Build base images

dev: .dev ## Install dev dependencies locally (includes pylint for in editor linting)

lint: .lint  ## Run lint (pylint, black, pycodestyle)

test: .test  ## Run tests

code: .lint .test  ## Run both lint and tests

kill:  ## Stop all running services
	docker-compose down

# --- local deploy --- #
deploy-role ?= $(DEPLOY_ROLE)
gitsha := $(shell git rev-parse --short HEAD)
region := $(AWS_REGION)
ecr-registry ?=
jwt-secret := $(JWT_SECRET)
service := kolvir
serverless-env = \
	-e GITSHA=$(gitsha) \
	-e SERVICE=$(service) \
	-e JWT_SECRET=$(jwt-secret) \
	-e REGION=$(region)
serverless-params := --verbose
.serverless-env:
	$(eval account-id := $(patsubst "%",%,$(shell PYTHONPATH=$$(pwd) pipenv run \
		python ./kolvir/aws/assume_role.py \
		--role $(deploy-role) --mfa \
			aws sts get-caller-identity --query Account)))
	$(eval ecr-registry := $(account-id).dkr.ecr.$(region).amazonaws.com)

deploy: .build .dev .test .serverless-env ## Deploy from local
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/aws/assume_role.py --role $(deploy-role) --mfa \
		aws ecr get-login-password --region $(region) | \
			docker login --username AWS --password-stdin $(ecr-registry)
	docker build . -t kolvir:api -t kolvir \
		-t $(ecr-registry)/kolvir:$(gitsha) --target api --rm
	docker push $(ecr-registry)/kolvir:$(gitsha)
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/aws/assume_role.py --role $(deploy-role) --mfa \
		docker-compose run -e SLS_DEBUG=* $(serverless-env) --rm kolvir.$(context) \
			./node_modules/.bin/serverless deploy $(serverless-params)

container-id ?= new
bash: .build  ## Run bash in container [container-id=<an id>] otherwise in existing or new app container
ifeq ($(container-id), new)
	docker-compose run --rm kolvir.$(context) /bin/bash
else
	docker exec -it $(container-id)  /bin/bash
endif

ipython: .dev  ## Run ipython
	PYTHONPATH=$$(pwd) pipenv run ipython

token: .dev  ## Generate a JWT
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/token/generate.py \
		--scopes pypi

package: .dev  # Deploy the kolvir private pypi package to s3
	rm -rf kolvir.egg-info dist
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/aws/assume_role.py \
		--role $(deploy-role) --mfa \
			/bin/bash ./scripts/deploy.sh setup.py $(PYPI_S3_BUCKET)

serverless: .build .dev .test .serverless-env  # Create the Serverless Cloudformation
	rm -rf .serverless
	PYTHONPATH=$$(pwd) pipenv run python ./kolvir/aws/assume_role.py \
		--role $(deploy-role) --mfa \
		docker-compose run -e SLS_DEBUG=* $(serverless-env) --rm kolvir.$(context) \
			./node_modules/.bin/serverless package
