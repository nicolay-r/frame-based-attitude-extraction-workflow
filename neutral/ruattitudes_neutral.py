import os
import zipfile
from tqdm import tqdm

from core.source.synonyms import SynonymsCollection
from neutral.ext_auth_text_obj import ExtendedAuthTextObject
from neutral.log import Log
from neutral.opinion_stat import OpinionStatisticPrinter
from texts.printing.contexts import ContextsPrinter
from texts.printing.diffcontexts import DiffContextsPrinter
from texts.printing.utils import AttitudeDescriptionTemplate, AttitudeKey, ObjectKey, FrameVariantKey


class RuAttitudeExpansion(object):

    def __init__(self, ner_loc_type, locations_to_ignore):
        assert(isinstance(ner_loc_type, str))
        assert(isinstance(locations_to_ignore, set))

        self.__ner_loc_type = ner_loc_type
        self.__locations_syn_ids_to_ignore = None
        self.__locations_values_to_ignore = locations_to_ignore

        self.__used_locations = {}

    # region public methods

    def add_neutral(self,
                    from_zip_filepath,
                    to_zip_filepath,
                    log_filepath,
                    used_locations_filepath,
                    neut_opin_stat_filepath):
        assert(isinstance(from_zip_filepath, str))
        assert(isinstance(to_zip_filepath, str))
        assert(isinstance(log_filepath, str))
        assert(isinstance(used_locations_filepath, str))
        assert(isinstance(neut_opin_stat_filepath, str))

        with zipfile.ZipFile(from_zip_filepath, 'r') as zip_input:
            to_dir = os.path.dirname(to_zip_filepath)
            zip_input.extractall(to_dir)

            target_filepath = os.path.join(to_dir, "collection-neut.txt")
            with open(os.path.join(to_dir, "collection.txt"), 'r') as f_src:
                with open(target_filepath, 'w') as f_to:
                    log = self.__process(f_src=f_src, f_to=f_to)

                # Saving.
                target_zip = zipfile.ZipFile(to_zip_filepath, "w")
                target_zip.write(target_filepath)
                target_zip.close()

        # TODO. Read synonyms collection from here.
        synonyms = None

        return SynonymsCollection.from_file(
            filepath=filepath,
            stemmer=stemmer,
            is_read_only=True)

        self.__init_from_synonyms(synonyms)

        if log is not None:
            with open(log_filepath, 'w') as f:
                for line in log.iter_data():
                    f.write(line)

        with open(used_locations_filepath, 'w') as f:
            for key, value in sorted(self.__used_locations.items(), key=lambda pair: pair[1]):
                f.write("'{entry}': {count}\n".format(entry=key, count=value))

        self.__opin_stat_printer.print_statistic(neut_opin_stat_filepath)

    # endregion

    # region private methods

    def __init_from_synonyms(self, synonyms):
        assert(isinstance(synonyms, SynonymsCollection))

        self.__opin_stat_printer = OpinionStatisticPrinter(synonyms=synonyms)

        self.__locations_syn_ids_to_ignore = set(
            [synonyms.get_synonym_group_index(v)
             for v in self.__locations_values_to_ignore
             if synonyms.has_synonym(v)])

    def __process(self, f_src, f_to):
        processed_sentences = []
        opinions_list = []
        objects_list = []

        log = Log()

        docs_set = set()

        for line in tqdm(f_src.readlines(), ncols=80):

            if line.startswith(ContextsPrinter.FILE_KEY):
                _, value = line.split(':')
                value = value.strip()
                if value in docs_set:
                    print("Document is already presented before in collection: '{}'".format(value))
                docs_set.add(value)

            if DiffContextsPrinter.TEXT_KEY in line or \
               DiffContextsPrinter.TITLE_KEY in line:
                objects_list = []
                opinions_list = []

            if ObjectKey in line:
                obj = self.__parse_object(line)
                objects_list.append(obj)

            if AttitudeKey in line:
                opinion = RuAttitudeExpansion.__parse_sentence_opin(line)
                opinions_list.append(opinion)
                log.reg_existed_opin()

            if ContextsPrinter.NEWS_SEP_KEY.strip() in line:
                log.reg_doc()

            if FrameVariantKey in line:
                for pair in self.__provide_netral_opinion(objects_list, opinions_list):
                    s = self.__compose_and_register(s_obj=pair[0], t_obj=pair[1])
                    f_to.write(s)
                    log.reg_new_opin(1)

                log.reg_sent()

            f_to.write(line)

        assert(len(processed_sentences) == 0)
        return log

    def __compose_and_register(self, s_obj, t_obj):
        assert(isinstance(s_obj, ExtendedAuthTextObject))
        assert(isinstance(t_obj, ExtendedAuthTextObject))

        source_value = s_obj.get_value()
        target_value = t_obj.get_value()

        syn_s = s_obj.SynonymIndex
        syn_t = t_obj.SynonymIndex

        line = AttitudeDescriptionTemplate.format(
            template=AttitudeKey,
            source_value=source_value,
            target_value=target_value,
            sentiment='0',
            s_ind=s_obj.CollectionInd,
            t_ind=t_obj.CollectionInd,
            ss_ind=syn_s,
            st_ind=syn_t)

        self.__opin_stat_printer.register_opinion(
            source=source_value,
            target=target_value,
            key="{}_{}".format(syn_s, syn_t))

        return line

    def __provide_netral_opinion(self, objects_list, opinion_list):
        for i, a in enumerate(objects_list):
            for j, b in enumerate(objects_list):

                if i >= j:
                    continue

                o1 = objects_list[i]
                o2 = objects_list[j]

                if not self.__check_existed_and_correctness(opinion_list, obj_1=o1, obj_2=o2):
                    yield o1, o2

                if not self.__check_existed_and_correctness(opinion_list, obj_1=o2, obj_2=o1):
                    yield o2, o1

    def __check_existed_and_correctness(self, opinion_list, obj_1, obj_2):
        assert(isinstance(obj_1, ExtendedAuthTextObject))
        assert(isinstance(obj_2, ExtendedAuthTextObject))

        s1 = obj_1.SynonymIndex
        s2 = obj_2.SynonymIndex

        for pair in opinion_list:

            # Skip unknown
            if s1 < 0: # or s2 < 0:
                return True

            # Skip synonymous
            if s1 == s2:
                return True

            if self.__check_tartget_to_be_discarded(obj_2):
                return True

            if pair[0] == s1 and pair[1] == s2:
                return True

            if pair[1] == s1 and pair[0] == s2:
                return True

        return False

    def __check_tartget_to_be_discarded(self, obj):
        assert(isinstance(obj, ExtendedAuthTextObject))

        if obj.Type != self.__ner_loc_type:
            return True

        value = obj.get_value()
        if value in self.__locations_values_to_ignore:
            return True

        # Check also for subparts
        for token in value.split():
            if token in self.__locations_values_to_ignore:
                return True

        if obj.SynonymIndex in self.__locations_syn_ids_to_ignore:
            return True

        if value not in self.__used_locations:
            self.__used_locations[value] = 0
        self.__used_locations[value] += 1

        return False

    def __parse_object(self, line):
        assert (isinstance(line, str))

        line = line[len(ObjectKey) + 1:]

        s_from = line.index('b:(')
        s_to = line.index(')', s_from)
        position, _ = line[s_from+3:s_to].split(',')

        if 'oi:[' not in line:
            print(line)

        obj_ind_begin = line.index('oi:[', 0)
        obj_ind_end = line.index(']', obj_ind_begin + 1)
        collection_ind = int(line[obj_ind_begin+4:obj_ind_end])

        o_begin = line.index("'", 0)
        o_end = line.index("'", o_begin + 1)

        # id_in_sentence = int(line[obj_ind_begin + 4:obj_ind_end])
        value = line[o_begin + 1:o_end]

        is_auth = '<AUTH>' in line

        t_begin = line.index('type:')
        t_end = line.index('<', t_begin) if is_auth else len(line)
        obj_type = line[t_begin+5:t_end].strip()

        sg_from = line.index('si:{')
        sg_to = line.index('}', sg_from)
        group_index = int(line[sg_from + 4:sg_to])

        text_object = ExtendedAuthTextObject(terms=value.split(),
                                             position=int(position),
                                             obj_type=obj_type,
                                             is_auth=is_auth,
                                             description="",
                                             syn_ind=group_index,
                                             collection_ind=collection_ind)

        return text_object

    @staticmethod
    def __parse_sentence_opin(line):
        s_from = line.index('si:{')
        s_to = line.index('}', s_from)
        s_obj, t_obj = line[s_from + 4:s_to].split(',')
        return int(s_obj), int(t_obj)

    # endregion