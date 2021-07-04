#!/bin/bash
pushd .
cd scripts/synonyms/

  ROOT=../..
  VOCAB_DIR=$ROOT/data/.vocab

  mkdir -p $VOCAB_DIR

  python3 -u syn_0_extract_obj_values.py \
      --ner-type ontonotes-bert-mult --output-dir $VOCAB_DIR \
      --ner-cache-filepath $ROOT/data/cache/ner.sqldb \
      --source-dir $ROOT/data/source

  # Generates file synonyms.txt at output dir.
  python3 -u syn_1_compose_collection.py \
      --ru-thes-nouns $ROOT/synsets.N.xml \
      --obj-values-dir $VOCAB_DIR \
      --output-dir $ROOT/data/output
popd