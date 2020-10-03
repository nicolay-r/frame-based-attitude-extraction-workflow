import sys

sys.path.append('../')

from texts.ner_wraps.deep_ner import LocalDeepNERWrap
from core.processing.ner.obj_decs import NerObjectDescriptor


if __name__ == "__main__":

    ner = LocalDeepNERWrap()

    terms = "андрей сказал , что путин".split()
    infos = ner.extract([terms])

    print("Extracted objects:")
    for obj_desc in enumerate(infos):
        assert(isinstance(obj_desc, NerObjectDescriptor))
        l, r = obj_desc.get_range()
        print(terms[l:r], obj_desc.ObjectType)
