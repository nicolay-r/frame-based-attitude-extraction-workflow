import os
import zipfile
from os.path import basename, join, abspath


def get_target_filename(source_zip_filepath):
    # Extra information to be provided during processing.
    source_filename = basename(source_zip_filepath)
    source_filename_parts = source_filename.split('.')
    source_filename_parts[0] += '_neut'
    return '.'.join(source_filename_parts)


def archive_all_files_in_zip(to_zip_filepath, source_dir):
    with zipfile.ZipFile(to_zip_filepath, "w") as target_zip:
        for root, _, files in os.walk(source_dir):
            for filename in files:
                print("Archiving: '{}'".format(filename))
                target_zip.write(abspath(join(root, filename)), arcname=filename)
    print("Saving: {}".format(to_zip_filepath))
