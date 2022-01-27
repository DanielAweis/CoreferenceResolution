# class that reads in ConLL-Data and pre process it.
import DATA as DATA
import re

from DataReader.abstract_data_reader import AbstractDataReader


class CoNLLDataReader(AbstractDataReader):
    def __init__(self):
        super().__init__()
        # list of lists [file_path, document, gold]
        self.data = []

    def read_data_files(self, file_path):
        """Retrieves the file names if a folder was passed."""
        file_list = self.get_files_from_folder(file_path)
        for file in file_list:
            doc_tuple = self.read_file_in(file)
            # [file_path, document, gold]
            file_name = file.split("/")[-1]
            self.data.append([file_name, doc_tuple[0], doc_tuple[1]])

    def read_file_in(self, file_path):
        """Reads a file in and extracts relevant parts of the sentence blocks
        and the gold standard.

        :arg file (str)

        :return tuple((text, gold))
                - text: list(text) of
                        lists(sentences) of
                        tuples('0', 'In', 'IN', '(TOP(S(PP*')
                - gold: dict with keys = int and values = list of lists
                    {23: [[0, 23, 24],...], [[..],[..]], 12: [[2, 0, 5], ..]}
        """
        text = []
        gold = {}

        with open(file_path, 'r', encoding="utf-8") as f:
            lines_in_sentence = []

            for line in f:

                if line.startswith('#'):
                    continue

                if len(line) == 0 or line == '\n':
                    sentence_nr = len(text)
                    sentence_result_tuple = self.process_sentence_block(
                        lines_in_sentence, sentence_nr)

                    text.append(sentence_result_tuple[0])
                    lines_in_sentence.clear()

                    # gold result merging
                    gold_results_for_sentence = sentence_result_tuple[1]
                    for gold_nr in gold_results_for_sentence.keys():

                        list_for_gold_nr = []

                        if gold_nr not in gold:
                            gold[gold_nr] = list_for_gold_nr
                        else:
                            list_for_gold_nr = gold[gold_nr]

                        for sub_item in gold_results_for_sentence[gold_nr]:
                            list_for_gold_nr.append(sub_item)

                    continue

                lines_in_sentence.append(line)

        return tuple((text, gold))

    def process_sentence_block(self, lines_in_sentence, sentence_num):
        """Processes a block of on sentence from the Conell data, and stores
        this data in a list of tuples. Extracts the gold standard from the last
        line and stores it in a dictionary, which has an integer as key and a
        list of lists as value.

        Args:
            lines_in_sentence: list of raw lines of the ConLL Data
        ['bc/cctv/00/cctv_0000   8   0     This    DT    (TOP(S(NP*)     -    -   -   Speaker#1   *    (ARG1*)           *   -\n',
        'bc/cctv/00/cctv_0000   8   1       is   VBZ          (VP*      be  01   1   Speaker#1    *       (V*)           *   -\n',
        'bc/cctv/00/cctv_0000   8   2     what    WP   (SBAR(WHNP*)     -    -   -   Speaker#1    *    (ARG2*       (ARG1*)  -\n',
        'bc/cctv/00/cctv_0000   8   3       we   PRP        (S(NP*)     -    -   -   Speaker#1    *         *       (ARG0*)  -\n',
        'bc/cctv/00/cctv_0000   8   4     have   VBP          (VP*    have   -   -   Speaker#1    *         *            *   -\n',
        'bc/cctv/00/cctv_0000   8   5     seen   VBN          (VP*     see  01   3   Speaker#1    *         *          (V*)  -\n',
        'bc/cctv/00/cctv_0000   8   6    since    IN          (PP*      -    -   -   Speaker#1    *         *   (ARGM-TMP*   -\n',
        'bc/cctv/00/cctv_0000   8   7    1999     CD    (NP*)))))))     -    -   -   Speaker#1  (DATE)      *)           *)  -\n',
        'bc/cctv/00/cctv_0000   8   8        .     .            *))     -    -   -   Speaker#1    *         *            *   -\n']

            sentence_num: int

        Returns:
            tuple((lines, gold_nr_stacks_dict))
            - lines = list of tuple
            [('0', 'In', 'IN', '(TOP(S(PP*'),
            ('1', 'the', 'DT', '(NP(NP*'),
            ('2', 'summer', 'NN', '*)'), ...]

            - Data structure of the tuple:
                (index, token, pos-tag, part of tree)
                ('0', 'In', 'IN', '(TOP(S(PP*')

            - gold_nr_stacks_dict
            {18: [[1, 1, 1], [1, 5, 10]], 23: [[1, 14, 15]]}
        """
        lines = []
        gold_idx_list_dict = {}

        for line in lines_in_sentence:
            parts = line.split()
            # (index, token, pos-tag, part of tree)
            lines.append(tuple((parts[2], parts[3], parts[4], parts[5])))

            # last column is gold info
            gold_col_str = parts[-1].strip()
            row_nr = int(parts[2])
            self.append_gold_mentions(sentence_num, row_nr, gold_col_str, gold_idx_list_dict)

        return tuple((lines, gold_idx_list_dict))

    def append_gold_mentions(self, sentence_num, row_nr, gold_col_str, gold_idx_list_dict):
        """
        Appends gold mentions to a dictionary.

        :param sentence_num: The number of the sentence in this document
        :param row_nr: The row number of this row in the actual sentence
        :param gold_col_str: The last column of the conll-table, in which
                begin and end indices of mentions are defined
        :param gold_idx_list_dict: dict with list as values
        """
        # extract all beginning indices, like in '(23|(12' -> [23,12]
        begin_indices = self.extract_gold_start_indices(gold_col_str)

        for idx in begin_indices:
            if idx not in gold_idx_list_dict:
                # list of list because of multiple occurrences
                # of same gold nr in same sentence
                # [sentence_nr, start, end]
                gold_elems = [[sentence_num, row_nr, -1]]
                gold_idx_list_dict[idx] = gold_elems
            else:
                gold_elems = gold_idx_list_dict[idx]
                gold_elems.append([sentence_num, row_nr, -1])

        # extract all ending indices, like in '23)|12)' -> [23,12]
        end_indices = self.extract_gold_end_indices(gold_col_str)

        for idx in end_indices:
            gold_elems = gold_idx_list_dict[idx]
            gold_elems[-1][2] = int(row_nr)  # set end row

    @staticmethod
    def extract_gold_start_indices(gold_col_str):
        list_str = re.findall(r'\((\d+)', gold_col_str)
        list_int = [int(i) for i in list_str]
        return list_int

    @staticmethod
    def extract_gold_end_indices(gold_col_str):
        list_str = re.findall(r'(\d+)\)', gold_col_str)
        list_int = [int(i) for i in list_str]
        return list_int


def demo():
    dr = CoNLLDataReader()
    # dr.read_data(DATA.PATH_FLAT_DEV_one_text)
    dr.read_data_files("data")
    # data = [file_path, document, gold]
    # documents = list of sentences
    # sentences = list_of_sent_data: list of tuple
    # [('0', 'In', 'IN', '(TOP(S(PP*')]
    # (index of token, token, pos_tag, tree_part)
    # gold = {23: [[0, 23, 24], [1, 14, 15]],
    # [[..],[..]], 12: [[2, 0, 5], ..]}
    data = dr.data
    print(data[0][2])
    #print(list(data[0][2].values()))


if __name__ == '__main__':
    demo()
