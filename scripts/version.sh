#!/bin/bash

tag=$(git describe)
hash=$(git rev-parse --short HEAD)
version=${tag}-${hash}
if ! git diff --quiet HEAD --
then
    if [ ! -z ${VERBOSE+x} ]; then
        echo "Repo dirty!"
    fi
    version=${version}-dirty
fi
echo $version
