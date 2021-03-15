import wordcloud
import pandas as pd
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import nltk
from text_rank import remove_stopwords
nltk.download('punkt') # one time execution
# function to remove stopwords
nltk.download('stopwords')# one time execution


def clean_string(df):
    """
    clean_string takes a pandas dataframe and clean the titles stored in the dataframe and return a list of cleaned words
    """
    sentences = []
    for s in df['title'].unique():
      sentences.append(sent_tokenize(s))
    # flatten the list
    sentences = [y for x in sentences for y in x]
    # remove punctuations, numbers and special characters
    cleaned = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")
    cleaned = pd.Series(cleaned).str.replace("cell", " ")
    # make alphabets lowercase
    cleaned = [s.lower() for s in cleaned]
    stop_words = stopwords.words('english')
    # remove stopwords from the sentences
    cleaned = [remove_stopwords(r.split()) for r in cleaned]
    return cleaned


def create_cloud(cleaned,file_name):
    """
    create_cloud takes a list of cleaned words and generate wordcloud image
    """
    txt=''.join( cleaned)

    w = wordcloud.WordCloud(width=1000,
                            height=700,
                            background_color='white',
                            )

    w.generate(txt)

    w.to_file(file_name)

def start_word():
    df_name=input("What is the name of the csv file?")
    df=pd.read_csv(df_name)
    print ("CSV file read")
    cleaned=clean_string(df)
    print ("Text cleaned")
    file_name=df_name[:-3]+".png"
    create_cloud(cleaned,file_name)
    print("WordCloud created")
