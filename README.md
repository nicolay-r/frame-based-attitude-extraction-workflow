# Frame-Based Attitude Extraction Workflow

A source code for a core of news processing workflow.
It provides scripts for sentiment attitude extraction using frame-based method.

![](logo.png)


## Dependencies

* python == 3.6
* tqdm
* sqlite3
* AREkit == [0.19.5](https://github.com/nicolay-r/AREkit/tree/0.19.5-bdr-elsevier-2020-py3)
    * Utilized as a core library for text parsing, frames reading, stemming application, etc.
* ner == 0.0.2 
    * Optional, for `deep-ner` NER model
* deep-pavlov == 1.11.0 
    * Optional, for `bert-mult-ontonotes` NER model
    
# Collection Reader API

Please refer to the base class [API](texts/readers/base.py)

# Preparation pipeline order

1. NER cache;
2. Frames cache;
3. Synonyms collection.

## NER Cache development

**Problem:** BERT-based-ontonotes-mult model for NER (`deep-pavlov-1.11.0`), consumes a significant amount of time per a single document which 
reduces the speed in a whole text processing pipeline.

**Solution:** Employ a cache for NER results. We utilize `sqlite` as a storage for such data.

**Source:** `scripts/cache/ner` folder:

* `run_0_init.py` -- Database initialization (for a particular part/subfolder in a source);
* `run_1_gen_merge_sql.py` -- Generates sql script (`merge.sql`) for merging results of a separated `*.db` databases:

### NER Cache related Q/A

> How to gather all the databases in a single archive?
```
run_0_init.py ...  # providing related arguments.

cd <SOURCE_FOLDER>

tar -zcvf archive.tar.gz `find . -name *.db`
tar -xzvf archive.tar.gz <TEMP_DB_DIR>
```

> How to merge all the databases in a single one?
```
run_1_gen_merge_sql.py <TEMP_DB_DIR>

cd <TEMP_DB_DIR>

sqlite3
.read merge.sql
.quit
```


## Frames Cache development
> TODO.
>
## Synonyms Collection development
> TODO.

## References
> TODO.
