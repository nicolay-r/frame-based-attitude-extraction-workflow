#!/bin/bash
pushd .

  cd ../scripts/re/
  ROOT=../..

  python3 -u run_neut.py \
    --loc-type-string "[LOC]" \
    # Use your own path instead.
    --src-zip-filepath $ROOT"/data/ruattitudes-v1_2.zip" \
    --output-dir $ROOT"data/output/neut" \
    --states $ROOT"data/rus_states.lss" \
    --capitals $ROOT"data/rus_capitals.lss" \
    --ignored-objs $ROOT"data/rus_extra.lss"

popd
