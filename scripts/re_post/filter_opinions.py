import sys
import argparse

sys.path.append('../../')

from tqdm import tqdm
from os.path import join, basename, dirname
from core.evaluation.labels import NeutralLabel
from core.source.opinion import Opinion, OpinionCollection
from scripts.args.synonyms import SynonymsCollectionFilepathArg
from texts.extraction.first.utils import read_opinions
from texts.printing.statistics.base import OpinionStatisticBasePrinter
from texts.extraction.default import Default


def write_relevant(source_filepath, target_filepath, keys):
    assert(isinstance(source_filepath, str))
    assert(isinstance(target_filepath, str))
    assert(isinstance(keys, set))

    NEWS_SEP_KEY = '--------'

    with open(source_filepath, 'r') as input:
        with open(target_filepath, 'w') as output:
            for line in tqdm(input.readlines()):

                if NEWS_SEP_KEY in line:
                    skip_doc = False
                    continue

                if 'File:' in line:
                    key = line.split(':')[1].strip()
                    if key not in keys:
                        skip_doc = True
                    else:
                        output.write("{}\n".format(NEWS_SEP_KEY))

                if not skip_doc:
                    output.write("{}".format(line))


def iter_relevant_file_ids(source_filepath, opinions):
    assert(isinstance(opinions, OpinionCollection))

    with open(source_filepath, 'r') as f:

        current_file = None
        skip_doc = False

        for line in tqdm(f.readlines(), desc=source_filepath):

            if 'File:' in line:
                current_file = line.split(':')[1].strip()
                skip_doc = False

            if 'Attitude:' in line and not skip_doc:
                s_from = line.index(u"'")
                s_to = line.index(u"'", s_from+1)
                source_value = line[s_from+1:s_to]

                t_from = line.index(u"'", s_to+1)

                if "'" not in line[t_from+1:]:
                    print(line)

                t_to = line.index(u"'", t_from+1)
                target_value = line[t_from+1:t_to]

                o = Opinion(value_left=source_value,
                            value_right=target_value,
                            sentiment=NeutralLabel())

                if opinions.has_synonymous_opinion(o):
                    yield current_file
                    skip_doc = True


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Opinions filtering")

    parser.add_argument('--source-filepath',
                        dest='source_filepath',
                        type=str,
                        nargs='?',
                        help='Source directory')

    parser.add_argument('--opinion-stat-filepath',
                        dest='opinion_filepath',
                        type=str,
                        nargs='?',
                        help='Source directory')

    # Added parameters.
    SynonymsCollectionFilepathArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Readed parameters.
    opinion_filepath = args.opinion_filepath
    source_filepath = args.source_filepath
    synonyms_filepath = SynonymsCollectionFilepathArg.read_argument(args)
    opinion_filename = basename(opinion_filepath)

    stemmer = Default.create_default_stemmer()
    synonyms = Default.create_default_synonyms_collection(filepath=synonyms_filepath,
                                                          stemmer=stemmer)

    with open(opinion_filepath, 'r') as f:

        opinions = read_opinions(
            filepath=opinion_filepath,
            synonyms=synonyms,
            custom_opin_ends_iter=lambda use_sentiment: OpinionStatisticBasePrinter.iter_opinion_end_values(
                f=f, read_sentiment=use_sentiment),
            read_sentiment=False)

    file_ids_it = iter_relevant_file_ids(source_filepath=source_filepath,
                                         opinions=opinions)

    target_filepath = join(dirname(source_filepath), "{}-data.txt".format(opinion_filename))

    write_relevant(source_filepath=source_filepath,
                   target_filepath=target_filepath,
                   keys=set(file_ids_it))
