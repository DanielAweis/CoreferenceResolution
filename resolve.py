# Script to determine conference chains using the Multi-Sieve-Pass Algorithm.
from concurrent import futures
from concurrent.futures import Executor
from concurrent.futures.thread import ThreadPoolExecutor
import threading
import click
import json

# data reader and transformer
from DataReader.conll_data_reader import CoNLLDataReader
from DataReader.data_transformer import DataTranformer

# sieve classes
from MultiSievePassCorefResolution.Sieves.exact_match_sieve \
    import ExactMatchSieve
from MultiSievePassCorefResolution.Sieves.precise_construct_sieve \
    import PreciseConstructSieve
from MultiSievePassCorefResolution.Sieves.pronoun_sieve \
    import PronounSieve

# class dealing with the application of the sieves on the document object
from MultiSievePassCorefResolution.coreference_chain_resolver \
    import CoreferenceChainResolver


def create_json_file(dictionary, filename_out):
    """
    Parameter:
                dictionary : tokens are key, counts are values
                filename_out (str) : path to the result csv-file

    Create a json.file.
    """
    with open(filename_out, 'w',encoding='utf-8', newline='\n') \
            as json_file:
        json.dump(dictionary, json_file)


def exec(document, out_put_dir):
    """Running multiple threads. One document is one thread."""
    print(f"thread {threading.current_thread().getName()} "
          f"for file {document.path} started...")
    document.extract_mentions()

    # Instantiate sieve objects
    exact_sieve_pass = ExactMatchSieve()
    precise_construct_pass = PreciseConstructSieve()
    pronoun_sieve = PronounSieve()

    # Instantiate the CoreferenceChainResolver
    coref_chain_resolver = CoreferenceChainResolver()
    coref_chain_resolver.resolve(document, [exact_sieve_pass,
                                            precise_construct_pass,
                                            pronoun_sieve])

    # Apply all sieves on the document
    sieved_document_obj = coref_chain_resolver.sieve_mentions()

    # Get modified cluster from document
    clusters = sieved_document_obj.get_relevant_clusters()

    # Evaluation:
    f1_score = coref_chain_resolver.evaluate(document.gold)

    # save results in a json file
    out_put = dict()
    out_put["document"] = sieved_document_obj.path
    out_put["clusters"] = clusters
    out_put["f1"] = f1_score

    create_json_file(out_put, out_put_dir + "/output_"
                     + sieved_document_obj.path + ".json")
    print(f"thread {threading.current_thread().getName()} "
          f"for file {document.path}  finished!")


@click.command()
@click.option('-f', 'file_path', type=click.Path(exists=True),
              required=True, help='The file path (str) to the data.')
@click.option('-o', 'out_put_dir', type=click.Path(exists=True),
              required=True, help='The file path (str) were the output '
                                  'will be saved.')
def cli(file_path, out_put_dir):
    data_reader = CoNLLDataReader()
    data_reader.read_data(file_path)
    data = data_reader.data
    data_transformer = DataTranformer()
    transformed_data = data_transformer.create_document_objects_from_data(data)

    # thread pool for async processing of documents
    executor = ThreadPoolExecutor(max_workers=None, thread_name_prefix='COREF')

    # stores all submitted "future" objects
    future_list = []

    for document in transformed_data:
        # on every document
        # - sieves will be applied,
        # - f1 score calculated and
        # - json result written to file
        # in a separate thread managed by the thread pool
        future_list.append(executor.submit(exec, document, out_put_dir))

    # waiting for all submitted futures to be finished before
    # program will terminate
    for future in future_list:
        future.result()


def demo():
    # Instantiate a CoNLLDataReader object,
    #   - which reads the data in from a given data path.
    #   - The cleaned data is attribute from this class.
    # data = [[file_path, documents[list of sentences], gold_standard]
    dr = CoNLLDataReader()
    dr.read_data("DemoData/one_text")
    data = dr.data

    # Transforms data into a list of document objects.
    data_transformer = DataTranformer()
    transformed_data = data_transformer.create_document_objects_from_data(data)
    # Get out the mentions from the first document first sentence:
    # data = list of document objects
    # print(transformed_data[0].sentences[0].mentions)

    # Extract mentions for each document object
    for document in transformed_data:
        # Extracts all mention (all tagged NPs).
        # This will initialize also the clusters for the document,
        # bc all mention is first a cluster of its own.
        document.extract_mentions()
        # mention = dict of mention objects:
        # keys are the (sent_num, span_start, span_end)

        # print(document.clusters[0].mentions)

        # Cluster object:
        #   - ID = (int) a unique number to identify the cluster
        #   - information = (set) shared attributes a cluster has
        #   - head_mention_span:
        #       tuple(sent_num(int), span_start(int), span_end(int))
        #   - mentions = [list] of mentions, initialized with the head_mention
        #       - one mention be like : (0, 1, 5)
        #       - (sentence, span_start, span_end)

        # Instantiate sieve objects
        exact_sieve_pass = ExactMatchSieve()
        precise_construct_pass = PreciseConstructSieve()
        pronoun_sieve = PronounSieve()

        # Instantiate the CoreferenceChainResolver
        # First argument is a document object
        # Second argument is a list of sieve objects
        #   - They have to inherit from the AbstractSieve Class
        #   - The sieve method of the sieve objects will be applied the document
        #     object in order of the passed list of sieve objects
        coref_chain_resolver = CoreferenceChainResolver()
        coref_chain_resolver.resolve(document, [exact_sieve_pass,
                                                precise_construct_pass,
                                                pronoun_sieve])

        # Apply all sieves on the document
        sieved_document_obj = coref_chain_resolver.sieve_mentions()

        # Get modified cluster from document
        clusters = list(sieved_document_obj.get_clusters())
        for cluster in clusters:
            if len(cluster.mentions) > 1:
                print(cluster.mentions)

        # Evaluation:
        #   Pairwise F1 is used for evaluation, in which pairs are formed from
        #   mentions within each cluster (transitive shell), which are compared
        #   to the pairs of the gold standard. Singleton clusters containing only
        #   one mention, are ignored.

        # print(document.gold)
        # output: [[[0, 23, 24], [1, 14, 15], [4, 29, 30]],
        # [[9, 11, 12], [12, 10, 11]]]

        f1_score = coref_chain_resolver.evaluate(document.gold)
        print(f1_score)


if __name__ == "__main__":
    # If you want to run the demo, uncomment demo() and incomment cli()
    # demo()
    cli()
