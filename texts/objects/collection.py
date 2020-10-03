class TextObjectsCollection:

    def __init__(self, objects):
        assert(isinstance(objects, list))
        objects = sorted(objects, key=lambda text_object: text_object.Position)
        self.__ordered_objects = objects

    def get_object(self, index):
        return self.__ordered_objects[index]

    @classmethod
    def create_empty(cls):
        return cls([])

    def __iter__(self):
        for obj in self.__ordered_objects:
            yield obj

    def __len__(self):
        return len(self.__ordered_objects)
