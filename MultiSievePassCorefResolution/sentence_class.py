# This is a class which bundles all attributes of one sentence of a document.
from nltk import Tree


class Sentence:
    """
    - self.list_of_sent_data: list of tuple
        [('0', 'In', 'IN', '(TOP(S(PP*'), ...]
        (index of token, token, pos_tag, tree_part)
    - self.tree: nltk.Tree object
    - self.sentence_str: sentence as a string
    - self.mentions: list of mention information
        [[list_of_token], (span_start, span_end), [list_of_info]]
        [['the', 'summer', 'of', '2005'], (1, 5), ['DT', 'NN', 'IN', 'CD']]
    """
    def __init__(self, list_of_sent_data):
        self.list_of_sent_data = list_of_sent_data
        self.tree = self.__create_tree_obj()
        self.sentence_str = self.__create_sent_as_str()
        self.mentions = self.__extract_mentions()

    def get_sentence_as_str(self):
        return self.sentence_str.strip()

    def __create_sent_as_str(self):
        """Creates sentence as a string."""
        sentence = ""
        for elem in self.list_of_sent_data:
            sentence = sentence + " " + elem[1]

        return sentence.strip()

    def __create_tree_obj(self):
        """Creates a nltk Tree object."""
        sent_tree = ""
        for elem in self.list_of_sent_data:
            treepart = elem[3].replace("*", " " + elem[1])
            sent_tree = sent_tree + " " + treepart

        return Tree.fromstring(sent_tree)

    def __extract_mentions(self):
        """Extracts mentions from the nltk Tree.
        In this approach, it is assumed that each NP is a Mention.
        one mention be like:
            mention = [list_of_token, span_tuple, list_of_mention_info]
            [['the', 'summer', 'of', '2005'], (1, 5), ['DT', 'NN', 'IN', 'CD']]
        """
        mentions = []
        for s in self.tree.subtrees(lambda x: x.label() == "NP"):
            mention = s.leaves()
            span = self.__get_mention_span(mention)
            info = self.__extract_mention_information([mention, span[0]])
            mentions.append([mention, span[0], info])

        return mentions

    def __get_mention_span(self, mention):
        """Returns the mention span (indexes) as a tuple(span_start,span_end)."""
        sentence_tokenized = self.sentence_str.split()
        indexes = [(i, i+len(mention) - 1) for i in range(len(sentence_tokenized))
                   if sentence_tokenized[i:i+len(mention)] == mention]

        return indexes

    def __extract_mention_information(self, mention):
        """Extract the information for a mention. Returns a set."""
        # TODO: numerus (person, belebtheit?)
        # mention = [['the', 'summer', 'of', '2005'], (1, 5)]
        info = set()
        for i in range(mention[1][0],mention[1][1]):
            info.add(self.list_of_sent_data[i][2])

        return info

    def __get_list_of_leaves(self, list_of_trees):
        """Extract the list of leaves (token) for a given list of nltk Trees."""
        list_of_leaves = []
        for elem in list_of_trees:
            list_of_leaves.append(elem.leaves())

        return list_of_leaves

    def levelorder(self, left_to_right=True):
        """Method that traverses the nltk Tree of the sentence in levelorder.
        Returns the mentions in the order in which they were passed through
        as a list."""
        mentions = []
        if left_to_right:
            list_of_trees = self.__levelorder_left_to_right()
        else:
            list_of_trees = self.__levelorder_right_to_left()
        list_of_leaves = self.__get_list_of_leaves(list_of_trees)
        for mention in list_of_leaves:
            mention_span = self.__get_mention_span(mention)
            mentions.append(mention_span)

        return mentions

    def __levelorder_left_to_right(self):
        """Traverses the nltk tree in level order from left to right.
        Returns mention (NP) in order in which they were passed through
        as a list."""
        level_order = []

        queue = [self.tree]
        while len(queue) != 0:
            current_tree = queue[0]
            queue.pop(0)
            if isinstance(current_tree, str):
                continue
            for child in current_tree:
                queue.append(child)
                if not isinstance(child, str):
                    if child.label() == "NP":
                        level_order.append(child)

        return level_order

    def __levelorder_right_to_left(self):
        """Traverses the nltk tree in level order from right to left.
        Returns mention (NP) in order in which they were passed through
        as a list."""

        level_order = []

        queue = [self.tree]
        while len(queue) != 0:
            current_tree = queue[0]
            queue.pop(0)
            if isinstance(current_tree, str):
                continue

            for child in current_tree[::-1]:
                queue.append(child)
                if not isinstance(child, str):
                    if child.label() == "NP":
                        level_order.append(child)

        return level_order


def demo():
    one_sent = [('0', 'In', 'IN', '(TOP(S(PP*'),
                ('1', 'the', 'DT', '(NP(NP*'),
                ('2', 'summer', 'NN', '*)'),
                ('3', 'of', 'IN', '(PP*'),
                ('4', '2005', 'CD', '(NP*))))'),
                ('5', ',', ',', '*'),
                ('6', 'a', 'DT', '(NP(NP*'),
                ('7', 'picture', 'NN', '*)'),
                ('8', 'that', 'WDT', '(SBAR(WHNP*)'),
                ('9', 'people', 'NNS', '(S(NP*)'),
                ('10', 'have', 'VBP', '(VP*'),
                ('11', 'long', 'RB', '(ADVP*)'),
                ('12', 'been', 'VBN', '(VP*'),
                ('13', 'looking', 'VBG', '(VP*'),
                ('14', 'forward', 'RB', '(ADVP*)'),
                ('15', 'to', 'TO', '(S(VP*'),
                ('16', 'started', 'VBD', '(VP*'),
                ('17', 'emerging', 'VBG', '(S(VP*'),
                ('18', 'with', 'IN', '(PP*'),
                ('19', 'frequency', 'NN', '(NP*))'),
                ('20', 'in', 'IN', '(PP*'),
                ('21', 'various', 'JJ', '(NP*'),
                ('22', 'major', 'JJ', '*'),
                ('23', 'Hong', 'NNP', '(NML*'),
                ('24', 'Kong', 'NNP', '*)'),
                ('25', 'media', 'NNS', '*)))))))))))))'),
                ('26', '.', '.', '*))')]

    sent_obj = Sentence(one_sent)
    tree = sent_obj.tree
    print("NLTK-Tree:")
    tree.pretty_print()
    m = sent_obj.levelorder()
    print("Traverses the nltk Tree of the sentence in levelorder:")
    print(m)
    # [[(6, 25)], [(1, 4)], [(6, 7)], [(1, 2)], [(4, 4)],
    # [(9, 9)], [(19, 19)], [(21, 25)]]


if __name__ == '__main__':
    demo()
