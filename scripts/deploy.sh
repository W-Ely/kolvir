#!/bin/bash

# Deploy a package to private PyPI.

set -x -o errexit -o nounset -o pipefail

out_directory='dist'
setup_py=$1
s3prefix=$2
package_name=$(python "$setup_py" --name)
version=$(python "$setup_py" --version)
python "$setup_py" sdist -d "$out_directory"
package_path="$out_directory/$package_name-$version.tar.gz"
normalized_package_name=$(echo $package_name | tr '[:upper:]' '[:lower:]' | tr _ -)
normalized_package_file=$(basename $package_path | sed "s/^$package_name/$normalized_package_name/")
aws --region us-west-2 --sse=AES256 s3 cp $package_path $s3prefix/$normalized_package_name/${normalized_package_file}
