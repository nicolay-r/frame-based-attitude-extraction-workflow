import argparse
from os.path import join
from neutral.ruattitudes_neutral import RuAttitudeExpansion


def read_lss(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            data.append(line.strip().lower())

    return set(data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Enriching existed RuAttitudes Collection with neutral attitudes")

    src_zip_filepath = "../../ra_collections/ruattitudes-v1_2.zip"
    target_dir_default = "../../ra_colletions_out"

    ner_loc_type_string = u"[LOC]"

    data_dir = "../../data"
    default_states_filepath = join(data_dir, 'rus_states.lss')
    default_captitals_filepath = join(data_dir, 'rus_capitals.lss')
    default_extra_filepath = join(data_dir, "rus_extra.lss")

    parser.add_argument('--loc-type-string',
                        dest='loc_type_str',
                        type=str,
                        default=ner_loc_type_string,
                        nargs='?',
                        help='String that corresponds to location type of entity found by NER model (Default: "{}")'.format(ner_loc_type_string))

    parser.add_argument('--src-zip-filepath',
                        dest='src_zip_filepath',
                        type=str,
                        default=src_zip_filepath,
                        nargs='?',
                        help='Source collection zip archive (Default: "{}")'.format(src_zip_filepath))

    parser.add_argument('--output-dir',
                        dest='output_dir',
                        type=str,
                        default=target_dir_default,
                        nargs='?',
                        help='Output directory (Default: "{}")'.format(target_dir_default))

    parser.add_argument('--states',
                        dest='states',
                        type=str,
                        default=default_states_filepath,
                        nargs='?',
                        help='List of states of world countries (Default: "{}")'.format(default_states_filepath))

    parser.add_argument('--capitals',
                        dest='capitals',
                        type=str,
                        default=default_captitals_filepath,
                        nargs='?',
                        help='List of capitals of world countries (Default: "{}")'.format(default_captitals_filepath))

    parser.add_argument('--ignored-objs',
                        dest='ignored_objs',
                        type=str,
                        default=default_extra_filepath,
                        nargs='?',
                        help='Extra list of ignored objects (Default: "{}")'.format(default_extra_filepath))

    # Parsing input arguments.
    args = parser.parse_args()

    # Assigning parsed arguments.
    cache_dir = args.output_dir
    source_zip_filepath = args.src_zip_filepath
    states_filepath = args.states
    capitals_filepath = args.capitals
    objs_to_ignore_filepath = args.ignored_objs

    # Reading collections.
    capitals = read_lss(capitals_filepath)
    states = read_lss(states_filepath)
    objs_to_ignore = read_lss(objs_to_ignore_filepath)

    locations_to_ignore = set()
    locations_to_ignore = locations_to_ignore.union(capitals)
    locations_to_ignore = locations_to_ignore.union(states)
    locations_to_ignore = locations_to_ignore.union(objs_to_ignore)

    exp = RuAttitudeExpansion(ner_loc_type=ner_loc_type_string,
                              locations_to_ignore=locations_to_ignore)

    log_filepath = join(cache_dir, 'log.txt')
    log_locations_filepath = join(cache_dir, 'used_locations.txt')
    log_neut_opin_stat_filepath = join(cache_dir, 'neut_opin_stat.txt')

    exp.expand_with_neutral(from_zip_filepath=source_zip_filepath,
                            log_filepath=log_filepath,
                            cache_dir=cache_dir,
                            used_locations_filepath=log_locations_filepath,
                            neut_opin_stat_filepath=log_neut_opin_stat_filepath)
