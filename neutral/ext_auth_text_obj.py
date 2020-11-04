from texts.objects.authorized.object import AuthTextObject


class ExtendedAuthTextObject(AuthTextObject):

    def __init__(self, terms, position, is_auth, description, obj_type, collection_ind, syn_ind):
        super(ExtendedAuthTextObject, self).__init__(terms=terms,
                                                     position=position,
                                                     is_auth=is_auth,
                                                     obj_type=obj_type,
                                                     description=description,
                                                     collection_ind=collection_ind)

        self.__syn_ind = syn_ind

    @property
    def SynonymIndex(self):
        return self.__syn_ind
