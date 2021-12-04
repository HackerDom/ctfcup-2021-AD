#!/bin/bash

set -ex

for f in */requirements.txt; do
    pip3 install -r "$f";
done
