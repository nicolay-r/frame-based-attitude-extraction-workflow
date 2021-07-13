# Frame-Based Attitude Extraction Workflow

A source code for a core of news processing workflow.
It provides scripts for sentiment attitude extraction using frame-based method.

![](logo.png)


## Dependencies

* python == 3.6
* sqlite3
* arekit == [0.19.5](https://github.com/nicolay-r/AREkit/tree/0.19.5-bdr-elsevier-2020-py3)
    * Utilized as a core library for text parsing, frames reading, stemming application, etc.
* ner == 0.0.2 
    * Optional, for `deep-ner` NER model
* deep-pavlov == 1.11.0 
    * Optional, for `bert-mult-ontonotes` NER model
    
# Installation

* Step 1: Install dependencies.
``` bash
# Install AREkit dependency
git clone --single-branch --branch 0.19.5-bdr-elsevier-2020-py3 git@github.com:nicolay-r/AREkit.git core

# Download python dependencies
pip install -r requirements.txt
```
    
# Usage 

## Prepare data

1. Place the news collection at `data/source/`;
2. Download [RuWordNet](https://ruwordnet.ru/en/) and place at `data/thesaurus/`;
    - [Contact with authors to download]
3. Download [RuSentiFrames-2.0](https://github.com/nicolay-r/RuSentiFrames) collection;
```bash
cd data && ./download.sh
```
4. Provide news reader:
    - default news reader [[code]](texts/readers/simple.py)/[[sample]](data/source/sample.txt);
    - implement custom reader based on `BaseNewsReader` API.

## Apply processing

**Problem:** BERT-based-ontonotes-mult model for NER (`deep-pavlov-1.11.0`), consumes a significant amount of time per a single document which
reduces the speed in a whole text processing pipeline.

**Solution:** Employ a cache for NER results. We utilize `sqlite` as a storage for such data.

### Sentiment Attitude Annotation

Considered to run scripts which organized in the related [folder](scripts) in the following order:
1. Caching extracted data from document into sqlite tables:
    * NER data [[script]](step1_ner_cache.sh);
    * Frames data [[script]](step1_frames_cache.sh);
2. Gather synonyms collection [[script]](step2_cache_synonyms.sh):
    1. Extracting object values;
    2. Grouping into single synonyms collection.
3. Apply `re`script with `--task ext_by_frames` [[script]](step3_exatract_pairs.sh)
    * is a stage 1. of the workflow (pair list gathering)
4. Filter most relevant pairs from pair list [[script]](step4_filter_pairs.sh)
5. Apply `re` script with `--task ext_diff` [[script]](step5_extract_attitudes.sh)
    * is a stage 2. of the workflow.
    
### Expand with Neutral Attitude Annotation
6. Prepare archieved (`*.zip`) collection from step #5, which includes:
    * `synonym.txt` -- list of synonyms.
    * `collection.txt` -- RuAttitudes collection.
7. Run [[script]](step6_neutral_attitudes.sh)
    * Use `--src-zip-filepath` to pass the archived collection path from step #6.

## References
> To be added.
