### Q/A

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
