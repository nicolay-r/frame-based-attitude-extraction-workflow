from texts.objects.authorized.object import AuthTextObject


class TextObjectAuthorizer:

    def __init__(self, ner_type):
        l = [ner_type.get_person_type_str(),
             ner_type.get_geo_political_type_str(),
             ner_type.get_organization_type_str()]

        self.__supported_ner_types = set(l)

        print(self.__supported_ner_types)

    @property
    def SupportedNerTypesSet(self):
        return self.__supported_ner_types

    def is_auth(self, obj):
        assert(isinstance(obj, AuthTextObject) or obj is None)

        if obj is None:
            return False

        return obj.Type in self.__supported_ner_types
