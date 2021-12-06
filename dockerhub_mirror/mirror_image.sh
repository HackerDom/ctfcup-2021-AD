#!/bin/bash
set -e

REGISTRY=cr.yandex/crp43eatfi7j0r8lstl6

src=$1
dst="$REGISTRY/$1"

echo "Mirroring $src -> $dst"
docker pull $src \
  && docker tag "$dst" \
  && docker push "$dst"

