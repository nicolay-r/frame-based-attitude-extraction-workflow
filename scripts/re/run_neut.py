import argparse
import os
from os.path import join
import private.io_utils
from neutral.ruattitudes_neutral import RuAttitudeExpansion


def read_lss(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            data.append(line.strip().lower())

    return set(data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Enriching existed RuAttitudes Collection with neutral attitudes")

    ner_loc_type_string = u"LOC"
    synonyms = None
    source_dir = None
    target_dir = None
    states_filepath = join(private.io_utils.get_objects_root(), 'states.lss')
    capitals_filepath = join(private.io_utils.get_objects_root(), 'capitals.lss')
    extra_filepath = join(private.io_utils.get_objects_root(), 'extra.lss')

    source = join(source_dir, "ruattitudes-2.0.zip")
    target = join(target_dir, "ruattitudes-2.0-neut.zip")
    log = join(target_dir, 'log.txt')
    locations = join(target_dir, 'used_locations.txt')
    neut_opin_stat_filepath = join(target_dir, 'neut_opin_stat.txt')

    # Reading collections.
    capitals = read_lss(capitals_filepath)
    states = read_lss(states_filepath)
    extra = read_lss(extra_filepath)

    locations_to_ignore = set()
    locations_to_ignore = locations_to_ignore.union(capitals)
    locations_to_ignore = locations_to_ignore.union(states)
    locations_to_ignore = locations_to_ignore.union(extra)

    exp = RuAttitudeExpansion(ner_loc_type=ner_loc_type_string,
                              synonyms=synonyms)

    exp.add_neutral(from_zip_filepath=source,
                    to_zip_filepath=target,
                    log_filepath=log,
                    used_locations_filepath=locations,
                    neut_opin_stat_filepath=neut_opin_stat_filepath)
