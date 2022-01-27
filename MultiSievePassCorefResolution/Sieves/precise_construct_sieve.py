# The sieve links two referring expressions if they correspond to one of these
# constructions: Apposition, Predicative Nominative or Acronym.
from MultiSievePassCorefResolution.Sieves.abstract_sieve_class import AbstractSieve
import re


class PreciseConstructSieve(AbstractSieve):

    def is_compatible(self, mention, candidate, document_obj):
        """Checks if mention and candidate are compatible with each other.
        Case insensitive to also find matches that are at the beginning
        of the sentence. Returns True if so, otherwise returns False."""

        # prune search if a indefinite pronoun or indefinite article
        # implemented in the abstract class
        if self.__search_pruning(mention):
            return False

        # check if its an Acronym
        if self.__is_acronym(mention, candidate):

            return True

        # get sentence
        sentence = document_obj.sentences[mention.sent_num_span[0]].\
            get_sentence_as_str()

        candidate_str = candidate.get_mention_as_str()
        mention_str = mention.get_mention_as_str()

        # check if is a Predicative Nominative
        if self.__is_predicative_nominative(sentence, mention, candidate,
                                            mention_str, candidate_str):
            return True

        # check if it is a Apposition
        if self.__is_apposition(sentence, mention_str, candidate_str):

            return True

        # not Apposition, Predicative Nominative nor a Acronym
        else:

            return False

    @staticmethod
    def __is_apposition(sentence, mention_str, candidate_str):
        """Checks if the mention is a apposition of the candidate, based on the rule,
        that candidate (NP) and mention (NP) are separated by a comma."""
        reg_ex = candidate_str + ", " + mention_str + ", "
        if len(re.findall(reg_ex, sentence)) > 0:

            return True

        else:

            return False

    @staticmethod
    def __is_predicative_nominative(sentence, mention, candidate,
                                    mention_str, candidate_str):
        """Checks if is a Predicative Nominative based on a simple rule,
        that candidate (NP) and the mention (NP) are linked with a form
        of the verb to be. """

        # check if candidate and mention are from the same sentence
        if mention.sent_num_span[0] == candidate.sent_num_span[0]:
            # check if mention and candidate are linked with the verb "to be"
            to_be = [" am ", " are ", " is ", " was ", " were ",
                     " will be ", " has been ", " have been "]

            # check if a elem of to_be list is in sentence
            verb_is_in_sent = any(verb in sentence for verb in to_be)
            if verb_is_in_sent:
                # get verb
                for verb in to_be:
                    idx = sentence.find(verb)
                    if idx != -1:
                        combi = candidate_str + verb + mention_str
                        if combi in sentence:

                            return True
        else:

            return False

    def __is_acronym(self, mention, candidate):
        """Checks if mention or candidate is a acronym of the other."""

        # mention and candidate are tagged as nnp
        # and one is the acronym of the other one
        if "NNP" in mention.info and "NNP" in candidate.info:
            # convert all tokens to lower in both lists
            mention_list_lower = [item.lower() for item
                                  in mention.mention_token_list]
            candidates_list_lower = [item.lower() for item
                                     in candidate.mention_token_list]

            mention_acro = self.__get_acronym(mention_list_lower)
            candidate_acro = self.__get_acronym(candidates_list_lower)
            if mention_acro and candidate_acro:
                if mention_acro == candidates_list_lower \
                        or candidate_acro == mention_list_lower:

                    return True
        else:

            return False

    @staticmethod
    def __get_acronym(string_list):
        """Creates two acronyms, one dotted and another not."""
        letter_list = []
        for l in string_list:
            if l[0].isalpha():
                letter_list.append(l[0])
        if len(letter_list) == 1:
            letter_list = []
        return "".join(letter_list), (".".join(letter_list) + ".")
