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
4. Setup news reader:
    - [simple news reader](texts/readers/simple.py);
    - declare custom by nesting a base class.

## Apply processing

Considered to run scripts which organized in the related [folder](scripts) as follows:
1. `cache`  -- for caching extracted from document data into sqlite tables:
    * NER cache [[readme]](scripts/cache/ner/README.md);
    * Frames cache [PROVIDE TUTORIAL];
2. Gather synonyms collection [[script]](step2_cache_synonyms.sh):
    1. Extracting object values;
    2. Grouping into single synonyms collection.
3. Apply `re`script with `--task ext_by_frames` [[script]](step3_exatract_pairs.sh)
    * is a stage 1. of the workflow (pair list gathering)
4. Filter most relevant pairs from pair list [[script]](step4_filter_relevant_pairs.sh)
5. Apply `re` script with `--task ext_diff` [[script]](step5_extract_attitudes.sh)
    * is a stage 2. of the workflow.

## References
> To be added.
