# Transforms the data from an implemented data reader, which must inherit from
# the AbstractDataReader class (see data structure) into document objects

from MultiSievePassCorefResolution.document_class import Document
from MultiSievePassCorefResolution.sentence_class import Sentence


class DataTranformer:
    """This is a class that takes care of instantiating the data from the data
     reader object into a document object. this favors a modular extension of
     the program by other readers for other data, they only need to transform
     the data of the text into the form defined further below.

        # TODO: data must be in this data structure:
        # [inpath, [list of [list of documents[list of sentences]]], gold_standard]
        # file_path (str)
        # documents = list of sentences
        # sentences = list_of_sent_data = list of tuple
        # [('0', 'In', 'IN', '(TOP(S(PP*']
        # (index of token in the sentence, token, pos_tag, tree_part)"""

    @staticmethod
    def create_document_objects_from_data(data):

        list_of_document_objects = []
        list_of_sentences_objects = []
        for file_path, document, gold in data:
            for sentence in document:
                new_sent_obj = Sentence(sentence)
                list_of_sentences_objects.append(new_sent_obj)

            gold_standard = list(gold.values())
            new_document_obj = Document(file_path, list_of_sentences_objects, gold_standard)
            list_of_document_objects.append(new_document_obj)

        return list_of_document_objects
