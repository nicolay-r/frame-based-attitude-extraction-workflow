import sys

sys.path.append('../../../')

import argparse
from os.path import join
from texts.objects.cache.sqlite_ner_cache import SQLiteNERCacheData
from texts.readers.tools.utils import iter_all_subfiles


def write_for_filepath(filepath):
    return ["attach '{fp}' as toMerge;".format(fp=filepath),
            'BEGIN;',
            'insert into {table} select * from toMerge.{table};'.format(table=SQLiteNERCacheData.get_table_name()),
            'COMMIT;',
            'detach toMerge;']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cache combiner of multiple databases into a single one")

    parser.add_argument('source_dir',
                        type=str,
                        nargs=1,
                        help='folder with *.db sources')

    args = parser.parse_args()

    src_dir = args.source_dir[0]

    with open(join(src_dir, "merge.sql"), 'w') as sql_f:

        # Setting up a new database
        sql_f.write(".open merged.db\n")

        # Providing initial table creation script;
        create_table = SQLiteNERCacheData.CREATE_TABLE_IF_NOT_EXISTS_SQLITE_CMD.format(
            table=SQLiteNERCacheData.get_table_name())
        sql_f.write("{};".format(create_table.strip()))
        sql_f.write('\n')

        for filepath in iter_all_subfiles(data_folder=src_dir, data_folder_as_root=True):

            if '.db' not in filepath:
                continue

            content = write_for_filepath(filepath)
            for c in content:
                sql_f.write("{}\n".format(c))