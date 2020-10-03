from texts.printing.statistics.element import StatisticSentimentElement


def order_by_sentiment_and_amount(elem, total):
    assert (isinstance(elem, StatisticSentimentElement))

    if elem.Count == 0:
        return 0

    delta = round(get_elem_sentiment(elem), 3)
    delta += 0.001 * (float(elem.PositiveCount - elem.NegativeCount) / total)

    return delta


def get_elem_sentiment(elem):
    assert (isinstance(elem, StatisticSentimentElement))
    pos_percent, neg_percent = get_elem_pos_neg_sentiments(pos_count=elem.PositiveCount,
                                                           neg_count=elem.NegativeCount,
                                                           total=elem.Count)
    return pos_percent - neg_percent


def get_sentiment(pos_count, neg_count):
    pos_percent, neg_percent = get_elem_pos_neg_sentiments(pos_count=pos_count,
                                                           neg_count=neg_count,
                                                           total=pos_count + neg_count)
    return pos_percent - neg_percent


def get_elem_pos_neg_sentiments(pos_count, neg_count, total):

    pos_percent = get_element_sentimets_raw(count=pos_count, total=total)
    neg_percent = get_element_sentimets_raw(count=neg_count, total=total)

    return pos_percent, neg_percent


def get_element_sentimets_raw(count, total):
    return float(count) / total
