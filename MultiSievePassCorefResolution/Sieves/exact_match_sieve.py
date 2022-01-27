# Links two Referring Expressions if they match exactly the same string.
from MultiSievePassCorefResolution.Sieves.abstract_sieve_class import AbstractSieve


class ExactMatchSieve(AbstractSieve):

    def is_compatible(self, mention, candidate, document_obj):
        """Checks if mention and candidate are compatible with each other.
        Case insensitive to also find matches that are at the beginning
        of the sentence. Returns True if so, otherwise returns False. """

        # convert all tokens to lower in both lists
        mention_list_lower = [item.lower() for item
                              in mention.mention_token_list]
        candidates_list_lower = [item.lower() for item
                                 in candidate.mention_token_list]

        # check if its an exact match
        if mention_list_lower == candidates_list_lower \
                and mention.cluster_ID != candidate.cluster_ID:

            return True

        # if no exact match
        else:

            return False
