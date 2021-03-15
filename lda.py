from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
def topics(df):
    """
    topics function takes a pandas dataframe to and train a latent dirichlet allocation model on the titles in the dataframe
    """
    n_features = 1000
    tf_vectorizer = CountVectorizer(strip_accents = 'unicode',
                                    max_features=n_features,
                                    stop_words='english',
                                    max_df = 0.5,
                                    min_df = 10)
    tf = tf_vectorizer.fit_transform(df["title"])


    #n_topics = 5
    lda = LatentDirichletAllocation(n_components=5, max_iter=50,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(tf)
    n_top_words = 20
    tf_feature_names = tf_vectorizer.get_feature_names()
    print_top_words(lda, tf_feature_names, n_top_words)



def print_top_words(model, feature_names, n_top_words):
    """
    Print top words from the results
    """
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))

def start_lda():
    df_name=input("What is the name of the csv file?")
    print("CSV file read")
    df=pd.read_csv(df_name)
    print("Start LDA")
    topics(df)
