#!/bin/bash
pushd .

  cd ../scripts/re/
  ROOT=../..

  python3 -u run.py \
    --task ext_diff \
    --news-reader simple \
    --use-ner-cache-only \
    --ner-type ontonotes-bert-mult \
    --diff-pairs-list $ROOT/data/output/ext_by_frames/25-0.65-stat.txt \
    --ner-cache-filepath $ROOT/data/source/ner_cache_ontonotes-bert-mult.db \
    --frames-cache-dir $ROOT/data/source \
    --parse-frames-in-sentences \
    --synonyms $ROOT/data/synonyms/synonyms.txt \
    --output-dir $ROOT/data/output \
    --source-dir $ROOT/data/source
popd