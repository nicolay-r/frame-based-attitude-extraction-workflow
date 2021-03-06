import sys
import argparse
from os.path import join
from tqdm import tqdm

sys.path.append('../../')

from io_utils import create_dir
from scripts.args.out_dir import OptionalOutputDirArg
from scripts.synonyms.syn_0_extract_obj_values import WORD_TYPE_SEPARATOR
from texts.readers.tools.utils import get_all_subfiles
from texts.extraction.default import Default
from texts.objects.synonyms.ru_thes_synsets import RussianThesaurusSynsets


def iter_words_with_types_from_filepath(filename):
    with open(filename, 'r') as f:

        l_it = tqdm(f.readlines(),
                    desc=filename,
                    ncols=140)

        for line in l_it:
            params = line.split(WORD_TYPE_SEPARATOR)

            if len(params) != 2:
                continue

            obj_value, obj_type = params
            yield obj_value, obj_type


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create synonyms collection from list of words")

    parser.add_argument('--ru-thes-nouns',
                        dest='ruthes_filepath',
                        type=str,
                        nargs=1,
                        help='Russian thesaurus filepath (xml based file) for Nouns')

    parser.add_argument('--obj-values-dir',
                        dest='obj_values_dir',
                        type=str,
                        nargs=1,
                        help='Source dir')

    # Parse arguments.
    OptionalOutputDirArg.add_argument(parser)

    # Reading arguments.
    args = parser.parse_args()
    source_dir = args.obj_values_dir[0]
    output_dir = OptionalOutputDirArg.read_argument(args)

    # Initialize necessary instances for words grouping.
    stemmer = Default.create_default_stemmer()
    ruthes_nouns = RussianThesaurusSynsets.from_xml_file(filepath=args.ruthes_filepath[0])

    log_found_in_ruthes = 0
    log_lemmas_kept = 0
    syn_groups = {}

    # Processsing all the files in subdir.
    f_names_it = get_all_subfiles(data_folder=source_dir,
                                  f_name_check_rule=lambda _: True)
    for filename in f_names_it:
        print(filename)
        for obj_value, obj_type in iter_words_with_types_from_filepath(filename):

            if obj_value in ruthes_nouns:
                log_found_in_ruthes += 1
                group_value = ruthes_nouns[obj_value]
            else:
                log_lemmas_kept += 1
                group_value = obj_value

            group_value = group_value.strip()

            # Register value in result.
            if group_value not in syn_groups:
                d_s = set()
                d_s.add(group_value)
                syn_groups[group_value] = d_s

            syn_groups[group_value].add(obj_value)

    create_dir(output_dir)

    # Saving the result synonyms collection in cache dir.
    group_keys = syn_groups.keys()
    with open(join(output_dir, 'synonyms.txt'), 'w') as f:
        for g_key in reversed(sorted(group_keys, key=lambda k: len(syn_groups[k]))):
            value = syn_groups[g_key]
            f.write("{v}\n".format(v=",".join(value)))

    # Provide logging information in file.
    with open(join(output_dir, 'synonyms_log.txt'), 'w') as f:
        f.write("Total Processed: {}\n".format(log_lemmas_kept + log_found_in_ruthes))
        f.write("\tFound In RuThes: {}\n".format(log_found_in_ruthes))
        f.write("\tUsing Lemmas: {}\n".format(log_lemmas_kept))
        f.write("Entries added: {}\n".format(len(syn_groups)))
