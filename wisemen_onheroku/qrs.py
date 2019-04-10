from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from sklearn.neighbors import NearestNeighbors
from gensim.parsing.preprocessing import *
import numpy as np
import csv
import random
import warnings
import os
warnings.filterwarnings("ignore", category=FutureWarning)

# GLOBAL VARIABLES
quotes_db = []
d = 50 # Dimension of word vectors
quotes_file = "static/quotes_1939.csv"
k = 5

# LOADING PRETRAINED WORD VECTORS
# load the Stanford GloVe model
filename = 'static/glove_50d_uncompressed_short.bin'

# TIME TAKING OPERATION
#print("Loading Word2vec...Please wait...")
model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=100000)
#print("Loaded Word2vec.")

"""
#=========================================
#  Code to merge the part files of
#  Glove to form a one binary file.
#    Needed bcoz., the one was too big. (for git)
#-----------------------------------------

# Above would've worked, but GCP doesn't allow >32 MB file upload.
# so, I have breaked the glove.bin into 20MB files in `static/glove_parts/`,
# and I will join them to 'glove_uncompressed_joined.bin' file.
# Then load it.

filename = 'static/glove_uncompressed_joined.bin'

if not os.path.isfile(filename):  # only merge files if doesn't exist already.
  parts_prefix = 'static/glove_parts/glove_uncompressed_part_'

  with open(filename, 'ab') as full_file:
    for file_number in range(1,10):
      with open(parts_prefix + str(file_number), 'rb') as part_file:
        full_file.write(part_file.read())
        
model = KeyedVectors.load_word2vec_format(filename, binary=True)

#=========================================
"""

# SENTENCE TO VECTOR FUNCTION
def get_vec(any_string):
    """ Takes any string as input, and returns a representative vector.
      
      any_string -> list of words -> list of word2vec vecs -> sum of these vecs
                     -> a representative vec.
    
      Args:
        - any_string: str
      Reurns:
        - vec: (d,1) numpy vector.
    """
    
    # Step 1: Cleaning the string, and turning into a list of words.
    CUSTOM_FILTERS = [lambda x:x.lower(), strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric,remove_stopwords, strip_short]
    words = preprocess_string(any_string, CUSTOM_FILTERS)
    #DEBUG: print(words)
    
    # Exception 1: if preprocessing removes all the words
    #            act randomly:
    if not words:
        repr_vec = np.random.randn(d)
        return repr_vec
    
    
    # Step 2: Turning into list of word2vec vecs (ignoring words not in dictionary by representing them as zeros)
    vecs = [model[w] if w in model.vocab else np.zeros(d) for w in words ]
    
    # Return sum of these vecs i.e. representative vec
    repr_vec = sum(vecs)
    #DEBUG: print(repr_vec.shape, model.similar_by_vector(repr_vec, topn=1))
    
    # Exception 2: if sum is exactly zero, that means, no word was in vocab.
    #             so, do some hack here (ignorance is our hack).
    if sum(repr_vec == 0):
        repr_vec = np.random.randn(d)
    
    return repr_vec


# READING QUOTES FROM FILE
def readfile(filename):
    """ Return a list of lists (quotations). 
      Args:
        - filename: file of csv quotes file
                each line is of the format: "---quote---;--author--;--tag--"
      Returns:
        - quotes_db: a list of entries: each entry(list) contains data about that quotations.
    """
    
    quotes_db = []
    with open(filename) as csv_file:
        all_lines = csv.reader(csv_file, delimiter=';')        
        for line in all_lines:
            quote = line[0]
            auth = line[1]
            subject = line[2]
            vec = get_vec(quote + " " + subject)   # for each quotation, also compute its representative vector.
            quote_entry = [quote, auth, subject, vec]
            quotes_db.append(quote_entry)
    
    return quotes_db
    
quotes_db = readfile(quotes_file)

#print("Total number of quotations: ")
#print(len(quotes_db))


#################################
# MAIN FUNCTION
#############################
# THE CORE FUNCTION / SERVICE #
def seek_advice(query_string, num_quotes, usr_vec=""):
    """ Given a query string, return top n matching quotes.             
            [if some prior information about user's interest in terms
               of a vector is also available, then, that can also be used,]
    
      Args:
        - query_string: str: a sentence query (can also be another quotations)
        - num_quotes: int: number of top related quotations desired.
      Returns:
        - topk_quotes: list of entires: quotations and speakers.
    """
    
    ###############################################
    # Step 1. Turn the query string into vector.
    #
    #           vec(query) = sum(vec(all_its_words))
    ################################################  
    query_vec = get_vec(query_string)
    
    
    #################################################
    # Step 2. Retrieve top n 'similar' quotes which match this vector (+ usr_vec).
    #
    #            each quote -> stored as -> vec. [Globally defined]
    #            Use any 'similarity' metric between query_vec and quote_vecs
    #            for k-Nearest Neighbor.
    #####################################################
    samples = [ s[3] for s in quotes_db ] # getting only the quotation vectors
    
    # At max, 1000 quotations allowed (only). 
    k = num_quotes if num_quotes <= 1000 else 1000
    # In future extensions: 
    #   This can be a different policy decision too 
    #   (maybe based on SLA or user's quota).
    
    neigh = NearestNeighbors(k, radius=1.0, metric='cosine')
    neigh.fit(samples)
    
    # Simple version --------:
    #result = neigh.kneighbors([query_vec], k, return_distance=False)
    #result = result[0]
    
    # Shuffled version ----: (each time, a shuffled response, to deal with monotony)
    result = neigh.kneighbors([query_vec], k+5, return_distance=False)
    result = result[0]
    random.shuffle(result)
    result = result[:k]
    
    topk_quotes = [ { 'quote': quotes_db[i][0], 'author': quotes_db[i][1] } for i in result ]
    # only keep unique ones
    #DEBUG: print(topk_quotes)
    return topk_quotes
    
# DEMO
if __name__ == '__main__':
  recommends = seek_advice("what is life?", k)
  for q in recommends:
    print(q)
    
    


