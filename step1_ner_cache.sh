#!/bin/bash
pushd .
cd scripts/cache/ner

  ROOT=../..

  python3 -u run_0_init.py \
      --news-reader simple \
      --ner-type ontonotes-bert-mult \
      --source-dir $ROOT/data/source

  python3 -u run_1_gen_merge_sql.py \
      --source-dir $ROOT/data/source
popd
