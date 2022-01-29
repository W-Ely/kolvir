#!/bin/sh

set -ex

echo "pytest:"
pytest "$@" \
--showlocals \
--maxfail=1 \
--durations=10 \
--cov kolvir \
--color yes  \
--code-highlight yes \
--cov-report term-missing
