#!/bin/sh

set -eux

echo "serverless:"
"$(npm bin)"/serverless offline --allowCache

# event and header logs locally
# SLS_DEBUG="*" "$(npm bin)"/serverless offline --allowCache
