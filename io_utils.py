import os
from os.path import dirname


def get_data_root():
    return os.path.join(dirname(__file__), "text-processing-data/")


def get_relation_root(create=True):
    folder = os.path.join(get_data_root(), "Relations")
    if create:
        create_dir(folder)
    return folder


def get_objects_root(create=True):
    folder = os.path.join(get_data_root(), "Objects")
    if create:
        create_dir(folder)
    return folder


def get_context_root(create=True):
    folder = os.path.join(get_data_root(), "Contexts")
    if create:
        create_dir(folder)
    return folder


def create_dir(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
