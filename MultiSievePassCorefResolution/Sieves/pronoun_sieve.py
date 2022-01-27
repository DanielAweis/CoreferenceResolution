# The sieve links pronoun mentions to antecedents.
from MultiSievePassCorefResolution.Sieves.abstract_sieve_class import AbstractSieve


class PronounSieve(AbstractSieve):

    def is_compatible(self, mention, candidate, document_obj):
        """Checks if mention and candidate are compatible with each other.
        The pronoun sieve works on the basis of congruence features. If a
        mentions matches a cluster in the features, the mentions are linked.
        One characteristic is matched here: Numerus. Further features could
        be integrated in further work, like: Genus and Person or Animacy."""

        # prune search if a indefinite pronoun or indefinite article
        # implemented in the abstract class
        if self.__search_pruning(mention):
            return False

        # check if mention is a pronoun
        if mention.is_pronoun():
            if mention.is_plural():
                # check if candidate is plural
                if candidate.is_plural():

                    return True
            else:
                # check if candidate is not plural
                if not candidate.is_plural():

                    return True
        else:
            return False


