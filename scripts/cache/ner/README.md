## NER Cache development

**Problem:** BERT-based-ontonotes-mult model for NER (`deep-pavlov-1.11.0`), consumes a significant amount of time per a single document which 
reduces the speed in a whole text processing pipeline.

**Solution:** Employ a cache for NER results. We utilize `sqlite` as a storage for such data.

**Source:** `scripts/cache/ner` folder:

* `run_0_init.py` -- Database initialization (for a particular part/subfolder in a source);
* `run_1_gen_merge_sql.py` -- Generates sql script (`merge.sql`) for merging results of a separated `*.db` databases:

### NER Cache related Q/A

* How to gather all the databases in a single archive?
```
run_0_init.py ...  # providing related arguments.

cd <SOURCE_FOLDER>

tar -zcvf archive.tar.gz `find . -name *.db`
tar -xzvf archive.tar.gz <TEMP_DB_DIR>
```

* How to merge all the databases in a single one?
```
run_1_gen_merge_sql.py <TEMP_DB_DIR>

cd <TEMP_DB_DIR>

sqlite3
.read merge.sql
.quit
```
