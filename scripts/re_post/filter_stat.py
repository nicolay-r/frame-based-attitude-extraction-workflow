import sys
import argparse
from tqdm import tqdm
from os.path import dirname, join


sys.path.append('../../')

from scripts.args.synonyms import SynonymsCollectionFilepathArg
from texts.extraction.default import Default
from texts.printing.statistics.base import OpinionStatisticBasePrinter
from texts.printing.statistics.sort_utils import get_elem_pos_neg_sentiments


def is_save_elem(pos_count, neg_count, total, min_count, min_bound):
    return total >= min_count and max(list(get_elem_pos_neg_sentiments(pos_count=pos_count,
                                                                       neg_count=neg_count,
                                                                       total=total))) >= min_bound


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Statistics filtering")

    parser.add_argument('--stat-file',
                        dest='stat_filepath',
                        type=str,
                        nargs='?',
                        help='Source directory')

    parser.add_argument('--min-count',
                        dest='min_count',
                        default=1,
                        nargs='?',
                        type=int,
                        help='Minimal amount of attitudes to keep')

    parser.add_argument('--min-bound',
                        dest='min_bound',
                        default=0.65,
                        nargs='?',
                        type=float,
                        help='Min prob. of the related class (max by app for pos/neg).')

    parser.add_argument('--fast',
                        dest='fast',
                        nargs='?',
                        const=True,
                        default=False,
                        help='Filter stat rows only')

    parser.add_argument('-o',
                        dest='target_filepath',
                        type=str,
                        nargs='?',
                        help='Output filepath')

    SynonymsCollectionFilepathArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    synonyms_filepath = SynonymsCollectionFilepathArg.read_argument(args)
    min_count = args.min_count
    min_bound = args.min_bound
    source_filepath = args.stat_filepath
    is_fast_mode = args.fast

    print(args.target_filepath)

    target_filepath = join(dirname(source_filepath), "{}-{}-stat.txt".format(min_count, min_bound)) \
        if args.target_filepath is None else args.target_filepath

    # Providing cropped statistics.
    print("Target filepath: {}".format(target_filepath))

    if not is_fast_mode:
        # Normal mode. Might take significant amount of time.

        stemmer = Default.create_default_stemmer()
        print("Reading synonyms collection: {}".format(synonyms_filepath))
        synonyms = Default.create_default_synonyms_collection(filepath=synonyms_filepath,
                                                              stemmer=stemmer)

        print("Reading filepath: {}".format(source_filepath))
        printer = OpinionStatisticBasePrinter.from_file(filepath=source_filepath,
                                                        synonyms=synonyms)

        assert(0 <= min_bound <= 1)
        printer.save(is_save_elem=lambda elem: is_save_elem(total=elem.Count,
                                                            pos_count=elem.PositiveCount,
                                                            neg_count=elem.NegativeCount,
                                                            min_count=min_count,
                                                            min_bound=min_bound),
                     filepath=target_filepath,
                     write_header=False)
    else:
        # Fast mode.
        with open(target_filepath, 'w') as target:
            with open(source_filepath, 'r') as src:
                for args in tqdm(OpinionStatisticBasePrinter.iter_line_params(src)):
                    pos_count, neg_count, _, _, line = args

                    is_save = is_save_elem(total=pos_count + neg_count,
                                           pos_count=pos_count,
                                           neg_count=neg_count,
                                           min_count=min_count,
                                           min_bound=min_bound)

                    if not is_save:
                        continue

                    target.write(line)
