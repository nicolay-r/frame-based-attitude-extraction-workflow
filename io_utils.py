import os


def create_dir(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
