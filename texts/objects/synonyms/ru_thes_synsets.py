class RussianThesaurusSynsets:

    SYNSET_KEY_BEGIN = '<synset'
    SENSE_KEY_BEGIN = '<sense'
    GROUP_KEY_XML_ARG_TEMPLATE = 'ruthes_name="'

    def __init__(self, groups):
        assert(isinstance(groups, dict))
        self.value_to_group = groups

    @classmethod
    def from_xml_file(cls, filepath):

        val_to_group = {}

        current_synset = None

        with open(filepath, 'r') as f:
            for line in f.readlines():

                if cls.SYNSET_KEY_BEGIN in line and cls.GROUP_KEY_XML_ARG_TEMPLATE in line:
                    name = cls.__read_arg(line, cls.GROUP_KEY_XML_ARG_TEMPLATE)
                    current_synset = cls.__process_name(name).lower()
                    continue

                if cls.SENSE_KEY_BEGIN in line:
                    value = cls.__read_value(line).lower()
                    val_to_group[value] = current_synset
                    continue

        return cls(val_to_group)

    def __contains__(self, item):
        return item in self.value_to_group

    def __getitem__(self, item):
        return self.value_to_group[item]

    # region private methods

    @staticmethod
    def __process_name(synset):
        assert(isinstance(synset, str))

        for e in [',', '(']:
            if e in synset:
                synset = synset.split(e)[0]

        return synset

    @staticmethod
    def __read_value(line):
        return RussianThesaurusSynsets.__read_arg(line=line, template='>', end_template='<')

    @staticmethod
    def __read_arg(line, template, end_template='"'):
        if template not in line:
            return None
        begin = line.index(template) + len(template)
        end = line.index(end_template, begin)

        return line[begin:end]

    # endregion
