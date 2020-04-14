import re
import pandas as pd
from nltk.util import ngrams
import gensim.corpora as corpora
from gensim.models.phrases import Phrases, Phraser
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel, ldamodel

import spacy
from spacy.lemmatizer import Lemmatizer
from corpus import fr_core_news_sm


def clean_text(tweet):

    # Remove emojis and special characters from text
    if tweet.startswith('RT @'):
        tweet = re.sub('^RT @.+: ', '', tweet)
    tweet = re.sub('\n', ' ', tweet)
    tweet = re.sub('’', "'", tweet)
    tweet = re.sub('#', " ", tweet)
    tweet = re.sub("[^A-Za-z0-9éèàùâîôêûç ']+", '', tweet)
    #Replace accent
    ch1 = u"àâçéèêëîïôùûüÿ"
    ch2 = u"aaceeeeiiouuuy"
    s=""
    for c in tweet:
        i = ch1.find(c)
        if i>=0:
            s += ch2[i]
        else:
            s += c
    tweet=s
    return tweet


def read_tweets(file_path, from_date, to_date):
    #Read dataframe
    df = pd.read_csv(file_path, sep = ';')
    df = df[(df['date']>=from_date) & (df['date']<=to_date)]
    #Clean text
    df['tweet'] = df['tweet'].apply(lambda x: clean_text(x))
    return df

def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them. 
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)
    
def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True and not token.text.startswith(("ht","@"))]
    return doc

def make_ngrams(texts):
    bigram = Phrases(texts, min_count=1)
    bigram_mod = Phraser(bigram)
    trigram = Phrases(bigram[texts], min_count=1) 
    trigram_mod = Phraser(trigram)
    return [bigram_mod[doc] for doc in texts] + [trigram_mod[bigram_mod[doc]] for doc in texts]

nlp= spacy.load("fr_core_news_sm")
# The add_pipe function appends our functions to the default pipeline.
nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

def build_combined_corpus(df):
    tweet_list = []
    # Iterates through each article in the corpus.
    for doc in list(df['tweet']):
        # Passes that article through the pipeline and adds to a new list.
        pr = nlp(doc)
        tweet_list.append(pr)
    # Delete elements with only whitespaces
    tweet_list = [[ele for ele in sent if not re.match(r'[^\S\n\t]+',ele) and len(ele)>3] for sent in tweet_list]
    # n-grams
    ngrams_ = make_ngrams(tweet_list)
    # ID -> word
    words = corpora.Dictionary(ngrams_)

    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in ngrams_]
    return corpus, words 

def build_ngram_corpus(df, nbr_grams):
    tweet_list = []
    # Iterates through each article in the corpus.
    for doc in list(df['tweet']):
        # Passes that article through the pipeline and adds to a new list.
        pr = nlp(doc)
        tweet_list.append(pr)
    # Delete elements with only whitespaces
    tweet_list = [[ele for ele in sent if not re.match(r'[^\S\n\t]+',ele) and len(ele)>=3] for sent in tweet_list]
    for idx in range(len(tweet_list)):
        tweet_list[idx] = ["_".join(w) for w in ngrams(tweet_list[idx], nbr_grams)]
    #print(tweet_list)
    # ID -> word
    words = corpora.Dictionary(tweet_list)

    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in tweet_list]
    return corpus, words 

def lda_model(ngram_corpus, ngram_words, n_topics):
    return ldamodel.LdaModel(corpus=ngram_corpus,
                                           id2word=ngram_words,
                                           num_topics=n_topics, 
                                           random_state=2,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)