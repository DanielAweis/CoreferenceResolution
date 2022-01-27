# This is a class which bundles all attributes of a mention together.
# For this approch a mention is a NP (the summer of 2005).
# TODO: property decorator?


class Mention:
    """
    self.cluster_ID: int
    self.sent_num_span: (sentence, start, end) = (1, 3, 7)
    self.mention_token_list: ['the', 'summer', 'of', '2005']
    self.info: ['DT', 'NN', 'IN', 'CD']
    """
    def __init__(self, cluster_ID, sent_num_span, mention_token_list, info):
        self.cluster_ID = cluster_ID
        self.sent_num_span = sent_num_span
        self.mention_token_list = mention_token_list
        self.info = info

    def get_actual_sentence_num(self):
        sent_num = self.sent_num_span[0]
        return sent_num

    def get_previous_sentence_num(self):
        prev_sent_num = self.sent_num_span[0] - 1
        return prev_sent_num

    def get_span(self):
        return tuple((self.sent_num_span[1], self.sent_num_span[2]))

    def set_cluster_ID(self, new_ID):
        self.cluster_ID = new_ID

    def get_mention_as_str(self):
        return " ".join(self.mention_token_list).strip()

    def starts_with_an_indefinite_article(self):
        if self.mention_token_list[0].lower() == "a" or "as":
            return True
        else:
            return False

    def is_nominal(self):
        is_nominal = True
        if "PRP" in self.info:
            is_nominal = False

        return is_nominal

    def is_an_indefinite_pronoun(self):
        indefinite_pronouns = ["anybody", "anything", "either", "everyone",
                               "much", "neither", "nothing", "other", "someone",
                               "anyone", "each", "everybody", "everything",
                               "nobody", "no one", "somebody", "something",
                               "several", "both", "others", "few", "many",
                               "any", "all", "more", "some", "most", "none"]
        check = any(elem in self.mention_token_list for elem
                    in indefinite_pronouns)
        if check:
            return True
        else:
            return False

    def is_pronoun(self):
        if "PRP" in self.info or "PRP$" in self.info:
            return True
        else:
            return False

    def is_plural(self):
        pl_pronoun = ["we", "they", "us", "them",
                          "ours", "yours", "theirs"]
        lower_mention_tok_l = [tok.lower() for tok in self.mention_token_list]
        return any(pro_noun in lower_mention_tok_l for pro_noun in pl_pronoun)


def demo():
    ID = 2
    sent_num_span = (3, 1, 5)
    mention_token_list = ['the', 'summer', 'of', '2005']
    info = ['DT', 'NN', 'IN', 'CD']
    one_mention = Mention(ID, sent_num_span, mention_token_list, info)
    print(f"Is mention nominal? {one_mention.is_nominal()}")
    print(f"Is mention plural? {one_mention.is_plural()}")
    print(f"Is mention an indefinite pronoun? "
          f"{one_mention.is_an_indefinite_pronoun()}")
    print(f"Starts mention with an indefinite article? "
          f"{one_mention.starts_with_an_indefinite_article()}")


if __name__ == '__main__':
    demo()