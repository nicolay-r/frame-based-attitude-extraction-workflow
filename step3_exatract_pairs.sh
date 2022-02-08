#!/bin/bash
pushd .

  cd scripts/re/
  ROOT=../..

  python3 -u run.py \
      --task ext_by_frames \
      --use-ner-cache-only \
      --news-reader simple \
      --ner-type ontonotes-bert-mult \
      --ner-cache-filepath $ROOT/data/source/ner_cache_ontonotes-bert-mult.db \
      --frames-cache-dir $ROOT/data/source/ \
      --synonyms $ROOT/data/synonyms/synonyms.txt \
      --rusentiframes $ROOT/data/rusentiframes-20.json \
      --output-dir $ROOT/data/output \
      --source-dir $ROOT/data/source

popd