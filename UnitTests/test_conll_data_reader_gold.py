from unittest import TestCase

from DataReader.conll_data_reader import CoNLLDataReader


class TestCoNLLDataReaderGold(TestCase):

    def test_extract_gold_start_indices(self):
        dr = CoNLLDataReader()
        start_indices = dr.extract_gold_start_indices('(23')
        assert len(start_indices) == 1
        assert start_indices[0] == 23

        start_indices = dr.extract_gold_start_indices('(23|(12')
        assert len(start_indices) == 2
        assert start_indices[0] == 23
        assert start_indices[1] == 12

        start_indices = dr.extract_gold_start_indices('(23|(12|13)')
        assert len(start_indices) == 2
        assert start_indices[0] == 23
        assert start_indices[1] == 12

    def test_extract_gold_end_indices(self):
        dr = CoNLLDataReader()
        end_indices = dr.extract_gold_end_indices('(23')
        assert len(end_indices) == 0

        end_indices = dr.extract_gold_end_indices('23)')
        assert len(end_indices) == 1
        assert end_indices[0] == 23

        end_indices = dr.extract_gold_end_indices('(12|23)')
        assert len(end_indices) == 1
        assert end_indices[0] == 23

        end_indices = dr.extract_gold_end_indices('(23|(12|13)')
        assert len(end_indices) == 1
        assert end_indices[0] == 13

    def test_read_gold_standard(self):
        dr = CoNLLDataReader()
        file_result = dr.read_file_in("test_data/gold_test.v4_auto_conll")

        assert len(file_result) == 2
        gold_dict = file_result[1]
        assert isinstance(gold_dict, dict)
        assert len(gold_dict[23]) == 5

        # sentence #1
        assert gold_dict[23][0][0] == 0
        assert gold_dict[23][0][1] == 23
        assert gold_dict[23][0][2] == 24

        # sentence #2
        assert gold_dict[23][1][0] == 1
        assert gold_dict[23][1][1] == 14
        assert gold_dict[23][1][2] == 15

        # sentence #3
        assert gold_dict[23][2][0] == 4
        assert gold_dict[23][2][1] == 29
        assert gold_dict[23][2][2] == 30

        # sentence #4
        assert gold_dict[23][3][0] == 5
        assert gold_dict[23][3][1] == 8
        assert gold_dict[23][3][2] == 9

        # sentence #5
        assert gold_dict[23][4][0] == 6
        assert gold_dict[23][4][1] == 3
        assert gold_dict[23][4][2] == 4
