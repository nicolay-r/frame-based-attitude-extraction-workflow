#!/bin/bash
pushd .

  cd scripts/re/

  ROOT=../..

  python3 -u scripts/re/run.py \
      --task ext_by_frames \
      --use-ner-cache-only \
      --ner-type ontonotes-bert-mult \
      --ner-cache-filepath $ROOT/data/cache/ner.sqldb \
      --frames-cache-dir $ROOT/data/cache \
      --synonyms $ROOT/data/synonyms/synonyms.txt \
      --rusentiframes $ROOT/data/rusentiframes-20.json \
      --output-dir $ROOT/data/output \
      --source-dir $ROOT/data/source

popd