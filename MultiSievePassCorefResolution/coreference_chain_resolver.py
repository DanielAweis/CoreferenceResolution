from MultiSievePassCorefResolution.Sieves.abstract_sieve_class import AbstractSieve
from MultiSievePassCorefResolution.errors import InvalidSieveClassError
import itertools


class CoreferenceChainResolver:
    """Objects of this class will call individual sieve classes
    and apply the sieve method on one document object to extract
    the coreference chains from the given text.

    The multi-pass-sieve approach is a rule-based, that applies
    independent rules to the referring expressions extracted (mentions)
    from the document. Each sieve operates on the output of the previous
    one and each sieve decides for an expression whether it can be
    resolved or not, and if so, to which cluster it should be assigned.
    """

    def __init__(self):
        """
        data: document object
        sieve_objects: list of Sieve objects
        (that inherit from AbstractSieve Class)
        """
        self.document_obj = None
        self.sieve_objects = None

    def resolve(self, document_obj, sieve_objects):
        self.__verify_input(sieve_objects)

        self.document_obj = document_obj
        self.sieve_objects = sieve_objects

    @staticmethod
    def __verify_input(objects):
        if any([not isinstance(obj, AbstractSieve) for obj in objects]):
            raise InvalidSieveClassError(
                'Sieve objects must inherit from AbstractSieveClass.')

    def sieve_mentions(self):
        """Calls the sieve method that is defined in the abstract class (which
        expects the abstract method sieve to be implemented). Apply the sieve
        of each class to the document object, in the order in which the sieves
        are given in the list.

        :return: sieved_document_obj, where the cluster attribute were
            manipulated in order to do Coreference Resolution: referring
            expressions are grouped based on the underlying referent and the
            deterministic rules applied in the sieve classes methods: All
            expressions in a cluster refer to the same entity.
            The clusters in the cluster attribute of the document object
            representing the coreference chains.
        """

        for sieve_class in self.sieve_objects:
            sieved_document_obj = sieve_class.sieve(self.document_obj)

            return sieved_document_obj

    @staticmethod
    def create_pairwise_combination(lst):
        """Combines all elements of a list in pairs.
        :param  lst: (list) [(212, 3, 3), (212, 0, 0)]
        :return: pair_order_list [((212, 3, 3), (212, 0, 0))]
        """
        pairwise_ordered_list = []
        # if only one or less elements in list
        if len(lst) < 2:
            return pairwise_ordered_list

        pairwise_ordered_list = itertools.combinations(lst, 2)

        return list(pairwise_ordered_list)

    def create_transitive_shell(self, lst):
        """Forms the transitive shell, in which the elements within each cluster
        are formed into pairs.
        :param  lst: (list)
                [[[0, 23, 24], [1, 14, 15]], [[1, 1, 1], [1, 5, 10]]]
        :return: transitive_shell set of strings
                {'((0, 23, 24), (1, 14, 15))', '((1, 1, 1), (1, 5, 10))'}
        """
        transitive_shell = set()

        for cluster in lst:
            new_pairs = self.create_pairwise_combination(cluster)  # returns a list
            for pair in new_pairs:
                # replace to have the same structure in gold and in result
                transitive_shell.add(str(pair).replace("[", "(").replace("]", ")"))

        return transitive_shell

    def evaluate(self, gold):
        """Pairwise F1 is used for evaluation, in which pairs are formed from
        the mentions within each cluster (transitive shell), which are compared
        to the pairs of the gold standard. Singleton clusters containing only
        one mention, are ignored."""

        # gold be like
        #  [[[0, 23, 24], [1, 14, 15], [4, 29, 30]], [[9, 11, 12], [12, 10, 11]]]

        if len(gold) == 0:
            return "No gold standard!"

        # transitive shell for gold
        gold_transitiv_shell = self.create_transitive_shell(gold)

        result = []
        result_cluster = list(self.document_obj.clusters.values())
        for cluster in result_cluster:
            result.append(cluster.get_mentions())

        # transitive shell for result
        result_transitiv_shell = self.create_transitive_shell(result)

        true_positives = len(gold_transitiv_shell.intersection(result_transitiv_shell))
        false_negatives = len(gold_transitiv_shell) - true_positives
        false_positives = len(result_transitiv_shell) - true_positives

        f1_score = true_positives / (true_positives + 0.5 * (false_positives + false_negatives))

        return f1_score
