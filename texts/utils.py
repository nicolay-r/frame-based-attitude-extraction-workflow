from core.evaluation.labels import Label, PositiveLabel, NegativeLabel


def optional_invert_label(label, is_inverted):
    assert(isinstance(label, Label))
    assert(isinstance(is_inverted, bool))

    if not is_inverted:
        return label
    if isinstance(label, PositiveLabel):
        return NegativeLabel()
    elif isinstance(label, NegativeLabel):
        return PositiveLabel()
    raise Exception("Not supported label")

