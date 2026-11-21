#!/usr/bin/env bash
# Container entry point. Data lives in $SOUP_DATA (the mounted work/ folder).
#   run.sh            build the matrix if missing, then the streaming search (BUDGET seconds)
#   run.sh matrix     (re)build the law x structure matrix
#   run.sh test       pytest
#   run.sh stream     streaming search only
set -eu
cd /app
: "${SOUP_DATA:=/data}"
cmd=${1:-all}; [ $# -gt 0 ] && shift
build_matrix() { echo "building the law x structure matrix (all cores)..."; python3 -m soup.matrix; }
case "$cmd" in
  matrix) build_matrix ;;
  test) [ -f "$SOUP_DATA/M_law_major.npy" ] || build_matrix; exec python3 -m pytest "$@" ;;
  stream) exec python3 -m soup.stream.supervisor "$@" ;;
  all) [ -f "$SOUP_DATA/M_law_major.npy" ] || build_matrix; exec python3 -m soup.stream.supervisor "$@" ;;
  *) exec "$cmd" "$@" ;;
esac
