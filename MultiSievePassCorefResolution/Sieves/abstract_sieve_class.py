# Base class for the sieve classes. Abstract method is is_compatible()
# were the sieves have deterministic rules to decide if a mention and a
# candidate can be grouped in on cluster.
from abc import ABC, abstractmethod


class AbstractSieve(ABC):
    """Abstract Sieve class that forces all sieve classes to define a
    method 'sieve' which resolves the coreference chains applying its rule.
    """

    def sieve(self, document_obj):
        """Extracts possible candidates according to the syntactic structure:
            - from the same sentence or:
              candidates are sorted based on left-to-right breadth-first
              traversal of syntax tree
            - from the previous sentence:
              - if mention is nominal: Candidates are sorted based on
              right-to-left breadth-first traversal of the syntax tree.
              - if mention is pronominal: Candidates are sorted based on
              left-to right-breadth-first traversal of the syntax tree."""

        for mention in document_obj.mentions.values():

            # Each sieve always tries to resolve only first mention in a cluster:
            # check if mention is head_mention in a cluster:
            cluster_ID = mention.cluster_ID
            if cluster_ID in document_obj.clusters and \
                    document_obj.clusters[cluster_ID].head_mention_span \
                    == mention.sent_num_span:

                # check if mention is nominal or pronominal
                if mention.is_nominal():
                    left_to_right_traversal = True
                else:
                    left_to_right_traversal = False

                # candidates = list of mention objects
                # [candidates of same sentence, candidates of previous sentence]
                candidates = document_obj.get_candidates(mention,
                                                         left_to_right_traversal)

                for candidate in candidates:

                    # method specified in each sieve class
                    if self.is_compatible(mention, candidate, document_obj):
                        # print(f"M: {mention.sent_num_span}")
                        # print(f"C: {candidate.sent_num_span}")
                        document_obj.unify_clusters(mention, candidate)

        return document_obj

    @staticmethod
    def __search_pruning(mention):
        """Two mentions are not linked if the candidate is either an
        indefinite pronoun or begin with an indefinite article.
        """
        # returns True if begins with an indefinite article
        if mention.starts_with_an_indefinite_article():
            return True

        # returns True is an indefinite pronoun
        if mention.is_an_indefinite_pronoun():
            return True

        else:
            return False

    @abstractmethod
    def is_compatible(self, mention, candidate, document_obj):
        """Checks if mention and candidate are compatible with each other,
        depending on the specific rule of the sieve."""
        pass
