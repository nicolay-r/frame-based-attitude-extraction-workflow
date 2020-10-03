# -*- coding: utf-8 -*-
from os import path, walk


def get_all_subfiles(data_folder, f_name_check_rule=lambda f_name: True):
    """
    Get list of files in nested directories

    data_folder: string
       folder with nested files and dirs

    Returns
    -------
        filepaths: list of strings
    """
    assert(callable(f_name_check_rule))

    filepaths = []

    for root, _, files in walk(data_folder):
        filepaths += [path.join(root, f_name) for f_name in files
                      if f_name_check_rule(f_name)]

    return sorted(filepaths)


def iter_all_subfiles(data_folder, data_folder_as_root=False):
    assert(isinstance(data_folder, str))
    assert(isinstance(data_folder_as_root, bool))

    for root, _, files in walk(data_folder):
        for f in files:
            d = path.relpath(root, data_folder) if data_folder_as_root else root
            yield path.join(d, f)
