# Class in which data structure for data is defined, which should ensure that
# the data is in the correct form in order to transform it into document
# objects with the DataTransformer.
import os
from abc import ABC, abstractmethod


class AbstractDataReader(ABC):
    """This is an abstracted class for data reader classes. This is to ensure
    that the data is fitted into the following form to support the modularity
    of the program if further readers are to be implemented:

    # TODO: data must be in this data structure:
    # [file_path, [list of [list of documents[list of sentences]]], gold_stand.]
    # file_path (str)
    # documents = list of sentences
    # sentences = list_of_sent_data = list of tuple
    # [('0', 'In', 'IN', '(TOP(S(PP*']
    # (index of token in the sentence, token, pos_tag, tree_part)"""

    def __init__(self):
        self.data = []

    def read_data(self, file_path):
        """Reads the data from a file, raises a FileNotFoundError
        if the file does not exist.

        Args:
            file_path (str): json file

        Returns:
            a list of dictionaries
        """
        try:
            # checks if path is a file
            is_file = os.path.isfile(file_path)

            # checks if path is a directory
            is_directory = os.path.isdir(file_path)

        except FileNotFoundError:
            raise

        if is_file:
            self.read_file_in(file_path)

        if is_directory:
            self.read_data_files(file_path)

    @staticmethod
    def get_files_from_folder(folder_name):
        """
        Takes in a folder name as a str.
        Returns a list of all file names
        ending with .txt.
        """
        list_of_files = []
        for file in os.listdir(folder_name):
            list_of_files.append(folder_name + "/" + file)

        return list_of_files

    @abstractmethod
    def read_file_in(self, file):
        pass

    @abstractmethod
    def read_data_files(self, infile):
        pass
