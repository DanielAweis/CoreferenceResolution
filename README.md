# Coreference_Resolution 
Coreference_Resolution is a Python tool for doing simple 
rule-based coreference resolution based on the on the paper 
by Raghunathan et al. (2010), which presents a multi-pass sieve 
approach that extracts coreference chains - a group of mentions 
that belong together - from text using so-called sieves by applying 
deterministic rules.

# Installation

Make sure you install all the requirements plus python 3.8

# Usage

The program runs in the command line. Input path and output path can be relative or absolute 
path's but make sure the directory for the output exists.

`python resolve.py -f DemoData\one_text -o OutPut/test.json`

`Options:`

  `-f PATH  The file path (str) to the data.  [required]`
  
  `-o PATH  The file path (str) were the output will be saved. [required]`
  
  
## Data 

Data must be in CoNLL-Format. The data are brought into a data structure with 
the ConLLDataReader (for more information see AbstractDataReader) and then 
the data are transformed with the DataTransformer into the object-based data 
structure intended for the project. 

## Sieve

The CoreferenceChainResolver calls individual sieve classes
and apply the sieve method on one document object to extract
the coreference chains from the given text.

The multi-pass-sieve approach is a rule-based, that applies
independent rules to the referring expressions extracted (mentions)
from the document. Each sieve operates on the output of the previous
one and each sieve decides for an expression whether it can be
resolved or not, and if so, to which cluster it should be assigned.

For this project tree sieves has been implemented: Exact-Match-Sieve, 
Pronoun-Sieve and Precise-Construct-Sieve. 

The output is a sieved document object, where the cluster attribute were
manipulated in order to do Coreference Resolution: referring
expressions are grouped based on the underlying referent and the
deterministic rules applied in the sieve classes methods: All
expressions in a cluster refer to the same entity.
The clusters in the cluster attribute of the document object
representing the coreference chains.

# Evaluation

The program calculates the pairwise f1-score. 

# Output 

The Output will be saved into a json file per document, saved into an already existing directory.
Directory can be absolute or relative. The keys in the jsin dict are file_name, clusters in a list 
of listes of tuples (sent_num, span_start, span_end) and f1-score.  

# Modularity

The program is built in such a way that it can be extended very easily at the two essential points: 
Adding another reader for different data and adding more Sieve classes. For this only in each case 
at a place in the script resolve.py either the newly implemented sieve into the list of the sieves 
to be applied must be passed to the CoreferenceChainResolver. And in the case of a new DataReader, 
these would have to be brought into the form defined in the AbstractDataReader class and then passed 
to the DataTransformer, which then builds the object structures needed for the project. 


