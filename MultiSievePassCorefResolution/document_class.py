# This is a class which bundles all attributes of a document together.
# By definition, a read-in file corresponds to a document object.
from MultiSievePassCorefResolution.cluster_class import Cluster
from MultiSievePassCorefResolution.mention_class import Mention
from collections import OrderedDict


class Document:
    """
    self.mentions: dict of mention objects
        - keys are the (sent_num, span_start, span_end)
    self.sentences: list of sentence objects
    self.clusters: dict of cluster objects
        - keys are cluster_ID (int)
    self.gold: list of lists
        - [[[0, 23, 24], [1, 14, 15], [4, 29, 30]], [[9, 11, 12]]]
    """
    def __init__(self, path, sentences, gold):
        self.path = path
        self.mentions = OrderedDict()
        self.sentences = sentences
        self.clusters = {}
        self.gold = gold

    def extract_mentions(self):
        """Instantiate the mention objects from the list of sentence objects and
        initialize the cluster objects."""
        ID = 0
        for count, sent_obj in enumerate(self.sentences):
            for mention in sent_obj.mentions:
                # mention =
                # [['the', 'summer', 'of', '2005'], (1, 5), ['DT', 'NN', 'IN', 'CD']]
                mention_token_list = mention[0]
                span_start = mention[1][0]
                span_end = mention[1][1]
                sent_num_span = (count, span_start, span_end)
                info = mention[2]

                # instantiate mention object
                new_mention = Mention(ID, sent_num_span, mention_token_list, info)
                self.mentions[sent_num_span] = new_mention

                # instantiate cluster object
                # (ID, information, head_mention_span, head_mention)
                new_cluster = (ID, info, sent_num_span, mention_token_list)
                self.__initialize_cluster(new_cluster)
                ID += 1

    def __initialize_cluster(self, new_cluster):
        """Instantiate a new Cluster object and add to cluster dict."""
        ID = new_cluster[0]
        info = new_cluster[1]
        head_mention_span = new_cluster[2]
        mention_token_list = new_cluster[3]
        new_cluster = Cluster(ID, info, head_mention_span, mention_token_list)

        self.clusters[ID] = new_cluster

    def get_candidates(self, mention, left_to_right_traversal):
        """
        Extracts the potential coreference candidates for a mention based on
        the syntactic structure:

        1. In the same sentence:
            - Candidates in the same sentence are sorted based on left-to-right
            breadth-first traversal of the syntax tree.

        2. In the previous sentence:
            - Nominal Mentions: candidates are sorted based on right-to-left-
            Breadth-first traversal (right-to-left breadth-first traversal) of
            the syntax tree.

            - Pronominal Mentions: Candidates are sorted based on left-to-left
            breadth-first traversal of the left-to-right breadth-first traversal
            of the syntax tree.

        :param  mention: mention object
                left_to_right_traversal: bool
        :return: candidates: list of mention objects
        """
        candidates = []  # list of mention objects

        # candidates from same sentence
        # get the sentence number of the sentence in which the mention occurs
        act_sent_num = mention.get_actual_sentence_num()
        akt_sent_ordered_candidates = self.sentences[act_sent_num].levelorder(
            left_to_right_traversal)  # [[(0, 1)], [(3, 4)], [(6, 8)], [(9, 12)]]

        # get mention span to check, if candidates from same sentence
        # are reasonable, e.g. syntactically before the mention
        mention_span = mention.get_span()

        # get mention objects
        candidates_akt_sent = self.__fetch_candidates(act_sent_num,
                                                      akt_sent_ordered_candidates,
                                                      mention_span)
        candidates.extend(candidates_akt_sent)

        # candidates from previous sentence
        # get the sentence number of the previous sentence
        prev_sent_num = mention.get_previous_sentence_num()

        # if there is no previous sentence
        if prev_sent_num < 0:
            candidates_prev_sent = []

        else:
            prev_sent_ordered_candidates = \
                self.sentences[prev_sent_num].levelorder(left_to_right_traversal)
            candidates_prev_sent = \
                self.__fetch_candidates(prev_sent_num, prev_sent_ordered_candidates)

        candidates.extend(candidates_prev_sent)

        return candidates

    def __fetch_candidates(self, sent_num, list_of_spans, mention_span=None):
        """Retrieves the potential candidates from a sentence.
        So all mention objects from the sentence object."""
        mention_objects = []

        for elem in list_of_spans:
            new_candidate = self.mentions[(sent_num, elem[0][0], elem[0][1])]
            if mention_span:
                # filter out only the candidates from the same sentence
                # that were syntactically realized before the mention:
                if new_candidate.get_span() > mention_span:
                    mention_objects.append(new_candidate)
            else:
                mention_objects.append(new_candidate)

        return mention_objects

    def unify_clusters(self, mention, candidate):
        """Unifies two clusters and updates the cluster dict."""
        # get the ID's
        mention_cluster_ID = mention.cluster_ID
        candidate_cluster_ID = candidate.cluster_ID
        if candidate_cluster_ID not in self.clusters:
            return

        if mention_cluster_ID not in self.clusters:
            return

        # get the two clusters
        mention_cluster = self.clusters[mention_cluster_ID]
        candidate_cluster = self.clusters[candidate_cluster_ID]

        # integrate mentions from mention_cluster to candidate_candidates
        candidate_cluster.add_mentions(mention_cluster.get_mentions())

        # update the cluster dict
        self.__update_cluster_map(mention_cluster_ID)

    def __update_cluster_map(self, mention_cluster_ID):
        """Deletes a cluster from the map that has been unified
        into another cluster."""
        self.clusters.pop(mention_cluster_ID)

    def get_clusters(self):
        """Returns the clusters as a list of lists."""
        return self.clusters.values()

    def get_relevant_clusters(self, more_than=1):
        """Returns the relevant clusters as a list of lists.
        more_than is default by 1."""
        relevant_clusters = []
        clusters = list(self.get_clusters())
        for cluster in clusters:
            if len(cluster.mentions) > more_than:
                relevant_clusters.append(cluster.mentions)
        return relevant_clusters


