#!/bin/bash
pushd .
cd scripts/cache/frames/

  ROOT=../../..

  # Results will be saved at data/source
  python3 -u run_0_init.py \
      --news-reader simple \
      --ner-type ontonotes-bert-mult \
      --ner-cache-filepath $ROOT/data/source/ner_cache_ontonotes-bert-mult.db \
      --parse-frames-in-sentences \
      --rusentiframes $ROOT/data/rusentiframes-20.json \
      --source-dir $ROOT/data/source
popd
