# This is a class which bundles all attributes of a cluster together.
# A cluster groups the mentions matched by the implemented sieves.
# All expressions in a group refer to the same entity.


class Cluster:
    """
    self.ID: int
    self.information: set {'DT', 'NN', 'IN', 'CD'}
        - Cluster information consists, for example, of shared attributes, i.e.,
        the union set of necessary congruence markers, e.g., numerus.
        Conflicting values are also included, e.g. singular, plural, so that
        the cluster could later be merged with both singular and plural pronouns.
    self.head_mention_span: (sent_num, span_start, span_end)
    self.mentions: list of mention objects
    self.head_mention: ['the', 'summer', 'of', '2005']
    """

    def __init__(self, ID, information, head_mention_span, head_mention):
        self.ID = ID
        self.information = information
        self.head_mention_span = head_mention_span
        self.mentions = [head_mention_span]
        self.head_mention = head_mention

    def add_mentions(self, mentions):
        """Adds a mention to the mention list. Remember a Mention consists
        of a tuple of 3 integers (sentence_num, start_span, end_span)"""
        self.mentions.extend(mentions)

    def get_mentions(self):
        """Returns the mention list, which is a list of tuples like:
        (sentence_num, start_span, end_span)"""
        return self.mentions

