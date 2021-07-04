#!/bin/bash
pushd .

  cd scripts/re_post/
  ROOT=../..

  python3 -u filter_stat.py
       --min-bound 0.65 \
       --min-count 25 \
       --stat-file $ROOT/data/output/ext_by_frames/stat.txt \
       --synonyms $ROOT/data/synonyms \
       --fast
popd
