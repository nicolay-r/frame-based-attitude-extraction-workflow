# Frame-Based Attitude Extraction Workflow

A source code for a core of news processing workflow.
It provides scripts for sentiment attitude extraction using frame-based method.

![](logo.png)


## Dependencies

* python == 3.6
* tqdm >= 4.19.5
* sqlite3
* AREkit == [0.19.5](https://github.com/nicolay-r/AREkit/tree/0.19.5-bdr-elsevier-2020-py3)
    * Utilized as a core library for text parsing, frames reading, stemming application, etc.
* ner == 0.0.2 
    * Optional, for `deep-ner` NER model
* deep-pavlov == 1.11.0 
    * Optional, for `bert-mult-ontonotes` NER model
    
## Resources
* ###### [RuWordNet](https://ruwordnet.ru/en/) [Contact with authors to download]
* [RuSentiFrames-2.0](https://github.com/nicolay-r/RuSentiFrames)

# Installation

* Step 1: Install dependencies.
``` bash
# Install AREkit dependency
git clone --single-branch --branch 0.19.5-bdr-elsevier-2020-py3 git@github.com:nicolay-r/AREkit.git core

# Download python dependencies
pip install -r requirements.txt
```
* Step 2: Download `rusentiframes-20.json` lexicon:
```bash
cd data && ./download.sh
```
    
# Usage 

Considered to run scripts which organized in the related [folder](scripts) as follows:
* **Step 1.** `cache`  -- for caching extracted from document data into sqlite tables:
    * NER cache [[readme]](scripts/cache/ner/README.md);
    * Frames cache [[readme]](scripts/cache/frames/README.md);
* **Step 2.** Gather synonyms collection:
```
pushd .
cd ../scripts/synonyms/

python3 -u syn_0_extract_obj_values.py \
		--ner-type ontonotes-bert-mult --output-dir ./.vocab \
		--ner-cache-filepath <NER_CACHE_SQLITE3_DB> \
		--source-dir <SOURCE_DIR>

python3 -u syn_1_compose_collection.py \
		--ru-thes-nouns Thesaurus/synsets.N.xml \
		--obj-values-dir .vocab/ \
		--output-dir <OUTPUT_DIR>
popd
```
* **Step 3.** `re` -- perform relation extraction with `--task ext_by_frames` -- 
is a stage 1. of the workflow (pair list gathering):
```bash
python3 -u scripts/re/run.py \
	--task ext_by_frames \
	--use-ner-cache-only \
	--ner-type ontonotes-bert-mult \
	--ner-cache-filepath <PATH_TO_SQLITE3_DB> \
	--frames-cache-dir <FOLDER_THAT_CONTAINS_SQLITE3_DB> \  
	--synonyms <SYNONYMS_COLLECTION> \
	--rusentiframes ../../data/rusentiframes-20.json \
	--output-dir <OUTPUT_DIR> \
	--source-dir <SOURCE_COLLECTION_DIR>
```
* **Step 4.** Filter most relevant pairs from pair list:
```
python3 -u filter_stat.py --min-bound 0.65 --min-count 25 \
     --stat-file <OUTPUT_DIR>/ext_by_frames/stat.txt \
     --synonyms <SYNONYMS_COLECTION> \
     --fast
```
* **Step 5.** Apply `re` script with `--task ext_diff` -- 
is a stage 2. of the workflow:
```
python3 -u scripts/re/run.py \
	--task ext_diff \
	--use-ner-cache-only \
	--ner-type ontonotes-bert-mult \
	--diff-pairs-list <OUTPUT_DIR>/ext_by_frames/25-0.65-stat.txt \
	--ner-cache-filepath <PATH_TO_SQLITE3_DB> \
	--frames-cache-dir <FOLDER_THAT_CONTAINS_SQLITE3_DB> \  
	--parse-frames-in-sentences \
	--synonyms <SYNONYMS_COLLECTION> \
	--output-dir <OUTPUT_DIR> \
	--source-dir <SOURCE_DIR> 
```
    
## Default News Reader

Please refer to the [simple news reader](texts/readers/simple.py):
* Reading from a single file;
* Documents separation via `\n`;
* Every sentence at new line, where first one is a title.

> TODO#1. Provide example and simple reader.

## Optional: caching resources for processing speed enhancement 
3. Synonyms collection [[readme]](scripts/synonyms/README.md).

## References
> TODO.
