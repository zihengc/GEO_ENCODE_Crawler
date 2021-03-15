'''TextRank function is modeified from Joshi (2018) An introduction to Text Summarization using the TextRank Algorithm'''
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
import re
from nltk.corpus import stopwords
import os
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt') # one time execution
# function to remove stopwords
nltk.download('stopwords')# one time execution


print('Strat reading GloVe vectors')
# Extract word vectors
word_embeddings = {}
#Read the pretrained glove matrix
os.system("wget http://nlp.stanford.edu/data/glove.6B.zip")
os.system("gzip -d glove.6B.zip")
f = open('glove/glove.6B.100d.txt', encoding='utf-8')

for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float64')
    word_embeddings[word] = coefs
f.close()

def remove_stopwords(sen):
    stop_words = stopwords.words('english')
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new


def text_rank():
    """ high level function that takes a csv file that contains summary of all geo entries and rank the important sentence with a pretrained word similarity matrix from Pennington, Socher, and Manning (2014).
    Reference: Jeffrey Pennington, Richard Socher, and Christopher D. Manning. 2014. GloVe: Global Vectors for Word Representation. [pdf] [bib]
    Parameters
    ----------
    allgeo_name: string; name of a csv file

    returns
    ------

    """
    allgeo_name=input("What is the name of the csv file?")
    df=pd.read_csv(allgeo_name)

    print("Start TextRank")
    # split the the text in the articles into sentences
    sentences = []
    for s in df['title'].unique():
      sentences.append(sent_tokenize(s))
    # flatten the list
    sentences = [y for x in sentences for y in x]
    # remove punctuations, numbers and special characters
    cleaned = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")
    # make alphabets lowercase
    cleaned = [s.lower() for s in cleaned]
    stop_words = stopwords.words('english')
    # remove stopwords from the sentences
    cleaned = [remove_stopwords(r.split()) for r in cleaned]

    #Calculate the sentence vectors based on word vectors
    sentence_vectors = []
    n=0

    for i in cleaned:
        try:
            if len(i) != 0:
                v = sum([word_embeddings.get(w, np.zeros((100,)))/np.power(10,12) for w in i.split()])/(len(i.split()))
            else:
                v = np.zeros((100,))
            sentence_vectors.append(v)
            n+=1
            #print(n)
        except:
            continue
    # similarity matrix
    sim_mat = np.zeros([len(sentences), len(sentences)])

    n=0
    for i in range(len(sentences)):
      for j in range(len(sentences)):
        if i != j:
          sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
        n+=1
        #print(n)
    nx_graph = nx.from_numpy_array(sim_mat)
    scores = nx.pagerank(nx_graph)

    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)


    # Specify number of sentences to form the summary
    sn = 15

    # Generate summary
    for i in range(sn):
        print(ranked_sentences[i][1]+'\n')
        print("---------------------------------------"+'\n')

    f=open("top_sentences.txt","a")
    for i in range(30):
        print(ranked_sentences[i][1])
        try:
            f.write(ranked_sentences[i][1]+'\n')
        except:
            print("Encoding error!!!!!!!!!!!!!!")
        print("---------------------------------------"+'\n')
        f.write("---------------------------------------"+'\n')
    f.close()
