def tokens_to_terms(terms, tokens, labels):
    def __cur_term():
        return len(joined_tokens) - 1

    assert(len(labels) == len(tokens))

    terms_lengths = [len(term) for term in terms]
    print(terms_lengths)
    current_lengths = [0] * len(terms)
    joined_tokens = [[]]
    joined_labels = [[]]
    for i, token in enumerate(tokens):
        print(__cur_term(), current_lengths[__cur_term()], token)
        if current_lengths[__cur_term()] == terms_lengths[__cur_term()]:
            joined_tokens.append([])
            joined_labels.append([])
        joined_tokens[-1].append(token)
        joined_labels[-1].append(labels[i])
        current_lengths[__cur_term()] += len(token)

    print(joined_tokens)
    print(gather(joined_labels))


def gather(labels_in_lists):
    return [labels[0] if len(labels) == 1 else gather_many(labels)
            for labels in labels_in_lists]


def gather_many(labels):
    return 'O'


if __name__ == "__main__":

    terms = ["Aмир", "здесь", "sfdjsf;s"]
    tokens = ["Aмир", "здесь", "sfdjsf", ";", "s"]
    labels = ["B-OBJ", "O", "O", "O", "O"]
    tokens_to_terms(terms, tokens, labels)

