from glob2 import glob
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import xlwings as xw
from collections import defaultdict
import copy
from math import trunc
import email
import spacy
import tqdm
import gensim
import gensim.corpora as corpora
import nltk
import re

nlp=spacy.load("en_core_web_sm",disable=["tagger", "parser","ner"])  #Only Tokennize
plt.rc('font', size="12")

from gensim.utils import simple_preprocess
from nltk.tokenize import RegexpTokenizer
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'power', 'enron', 'energy', 'electricity', 'california', 'said', 'ees', 'state', 'would', 'utility', 'market', 'utilities', 'hou',
                 'ect', 'davis', 'price', 'prices', 'gas', 'new', 'na', 'company', 'could', 'plants', 'pg', 'pm', 'corp', 'one', 'edison', 'may', 'email', 'ferc', 'billion', 'million', 'also', 'commission',
                 'generator', 'generators', 'san', 'enroncom', 'cc', 'electric', 'iso', 'us', 'blackouts', 'last', 'kean', 'enronxgate', 'year', 'two', 'time'])

def get_labels(filename):
    with open(filename + '.cats') as f:
        labels = defaultdict(dict)
        line = f.readline()
        while line:
            line = line.split(',')
            top_cat, sub_cat, freq = int(line[0]), int(line[1]), int(line[2])
            labels[top_cat][sub_cat] = freq
            line = f.readline()
    return dict(labels)

def nlp_tokenize_lower(string):
    return [token.text.lower() for token in nlp(string)]

def read_email_file(filename):
    with open(filename) as f:
        message = email.message_from_file(f)
    return message

def preprocess(filename):
    message=read_email_file(filename)
    file_categories = get_labels(filename[:-4])
    isPersonal = 0
    if 1 in file_categories:
        if 2 in file_categories[1] or 3 in file_categories[1]:
            isPersonal = 1
    words = []
    message_count = 1
    include_text = True
    body = message.get_payload()
    for line in body.split('\n'):
        message_count += 1
        include_text = False
        words.extend(nlp_tokenize_lower(line))
    
    return {"File":filename, "To":message['To'], "From":message['From'],"body":body,"message":words, "count": message_count, "IsPersonal": isPersonal}

def lemmatize(x):
    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in x])

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc))
            if word not in stop_words] for doc in texts]

def main():

    id_to_top_cat={1: "Coarse genre",
         2: "Included/forwarded information",
         3: "Primary topics",
         4: "Emotional tone"}

    id_to_sub_cat={1: {1: "Company Business, Strategy",
             2: "Purely Personal",
             3: "Personal but in professional context",
             4: "Logistic Arrangements",
             5: "Employment arrangements",
             6: "Document editing/checking",
             7: "Empty message (missing attachment)",
             8: "Empty message"},

         2: {1 : "Includes new text in addition to forwarded material",
             2 : "Forwarded email(s) including replies",
             3 : "Business letter(s) / document(s)",
             4 : "News article(s)",
             5 : "Government / academic report(s)",
             6 : "Government action(s)",
             7 : "Press release(s)",
             8 : "Legal documents",
             9 : "Pointers to url(s)",
             10: "Newsletters",
             11: "Jokes, humor (related to business)",
             12: "Jokes, humor (unrelated to business)",
             13: "Attachment(s) (assumed missing)"},

         3:{ 1  : "regulations and regulators (includes price caps)",
             2  : "internal projects -- progress and strategy",
             3  : "company image -- current",
             4  : "company image -- changing / influencing",
             5  : "political influence / contributions / contacts",
             6  : "california energy crisis / california politics",
             7  : "internal company policy",
             8  : "internal company operations",
             9  : "alliances / partnerships",
             10 : "legal advice",
             11 : "talking points",
             12 : "meeting minutes",
             13 : "trip reports"},

         4:{ 1  : "jubilation",
             2  : "hope / anticipation",
             3  : "humor",
             4  : "camaraderie",
             5  : "admiration",
             6  : "gratitude",
             7  : "friendship / affection",
             8  : "sympathy / support",
             9  : "sarcasm",
             10 : "secrecy / confidentiality",
             11 : "worry / anxiety",
             12 : "concern",
             13 : "competitiveness / aggressiveness",
             14 : "triumph / gloating",
             15 : "pride",
             16 : "anger / agitation",
             17 : "sadness / despair",
             18 : "shame",
             19 : "dislike / scorn"}}

    email_files = [f.replace('.cats', '') for f in glob('/Classifier_website/personal_classifier/python_files/enron_with_categories/*/*.cats')]

    content=[]
    for f in tqdm.tqdm(email_files):
        content.append(preprocess(f+".txt"))

    vocab={}
    for c in tqdm.tqdm(content):
        for w in c["message"]:
            if w in vocab:
                vocab[w]+=1
            else:
                vocab[w]=1

    Personal = []
    NonPersonal = []
    for c in content:
        if c['IsPersonal'] == 1:
            Personal.append(c)
        else:
            NonPersonal.append(c)

    Personaldf = pd.DataFrame(Personal)
    NonPersonaldf = pd.DataFrame(NonPersonal)

    Personaldf['category'] = 'Personal'
    NonPersonaldf['category'] = 'Non Personal'

    df_list = [Personaldf, NonPersonaldf]
    df = pd.concat(df_list).reset_index(drop=True)

    df['lemma'] = df['message'].map(lemmatize)

    X = df['lemma']
    Y = df['IsPersonal']

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=13)

    pipe_rf = Pipeline(memory=None,
                    steps=[('tf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
                     ('rf', RandomForestClassifier())],
                     verbose=False)
    pipe_rf.fit(X_train, Y_train)
    feature_names = (pipe_rf.named_steps["tf"].get_feature_names())
    coefs = (pipe_rf.named_steps["rf"].feature_importances_)

    zip_features = zip(feature_names,coefs)
    sorted_features = sorted(zip_features,key=lambda x: x[1], reverse=True)

    preds_rf = pipe_rf.predict(X)

    df['preds_rf'] = preds_rf

    topic_model = pd.DataFrame(content)
    topic_model = topic_model.drop(columns=['count', 'IsPersonal'])

    topic_model['body_processed'] = \
    topic_model['body'].map(lambda x: re.sub('[,\.!?-]', '', x))
    topic_model['body_processed'] = \
    topic_model['body_processed'].map(lambda x: x.lower())#

    data = topic_model.body_processed.values.tolist()
    data_words = list(sent_to_words(data))

    data_words = remove_stopwords(data_words)

    id2word = corpora.Dictionary(data_words)
    texts = data_words

    corpus = [id2word.doc2bow(text) for text in texts]

    num_topics = 10

    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                            id2word=id2word,
                                            num_topics=num_topics)

    doc_lda = lda_model[corpus]

    topic_names = []
    for i in range(0,num_topics):
        if lda_model.show_topic(i)[0][0] not in topic_names:
            topic_names.append(lda_model.show_topic(i)[0][0])
        else:
            topic_names.append(lda_model.show_topic(i)[0][0] + " " + lda_model.show_topic(i)[1][0])

    assign_topics = pd.DataFrame()
    for i, rowlist in enumerate(doc_lda):
        topic = 0
        percentage = 0
        for row in rowlist:
            if row[1] > percentage:
                topic = topic_names[row[0]]
                percentage = row[1]
        assign_topics = assign_topics.append(pd.Series([topic, round(percentage,4)]), ignore_index=True)
    assign_topics.columns = ['Topic', 'Percentage']

    df = pd.concat([df, assign_topics], axis=1)

    df.to_excel('classifier_data.xlsx')

    topic_content = []
    for i in range(0, num_topics):
        topic_content.append(lda_model.show_topic(i))
    

    return len(df.loc[df['preds_rf'] == 1]), pipe_rf.score(X_test, Y_test), sorted_features[:300], topic_content, topic_names