from core.runtime.object import TextObject


class AuthTextObject(TextObject):

    def __init__(self, terms, position, is_auth, obj_type, description, collection_ind):
        assert(isinstance(description, str))
        assert(isinstance(obj_type, str))
        assert(isinstance(collection_ind, int) and collection_ind >= 0)

        super(AuthTextObject, self).__init__(terms=terms,
                                             position=position)
        self.__is_auth = is_auth
        self.__description = description
        self.__obj_type = obj_type
        self.__collection_ind = collection_ind

    @property
    def IsAuthorized(self):
        return self.__is_auth

    @property
    def Description(self):
        return self.__description

    @property
    def Type(self):
        return self.__obj_type

    @property
    def CollectionInd(self):
        return self.__collection_ind

    @classmethod
    def create(cls, lemmas, position, obj_type, description, is_object_auth, collection_ind):
        assert(callable(is_object_auth))

        instance = cls(terms=lemmas,
                       position=position,
                       is_auth=True,
                       obj_type=obj_type,
                       description=description,
                       collection_ind=collection_ind)

        instance.__is_auth = is_object_auth(instance)

        return instance
