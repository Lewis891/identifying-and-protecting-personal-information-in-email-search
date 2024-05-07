import glob
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
nlp=spacy.load("en_core_web_sm",disable=["tagger", "parser","ner"])  #Only Tokennize
plt.rc('font', size="12")

from nltk.tokenize import RegexpTokenizer
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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

def check_category(filename, top_cat, sub_cat):
    labels = get_labels(filename)
    if sub_cat in labels[top_cat]:
        return 1
    return 0

def get_binary_labels(filenames, top_cat, sub_cat):
    flags = []
    for filename in filenames:
        flags.append(check_category(filename, top_cat, sub_cat))
    return flags

def plot_freq(x_dict,cnt_dict,figsize=(10,5),xlabel="",title=""):
    x,y=[],[]
    for k,v in x_dict.items():
        x.append(v)
        y.append(cnt_dict[k])
    y=np.array(y)
    y_srt=np.argsort(y)
    x=np.array(x)[y_srt]
    y=y[y_srt]
    plt.figure(figsize=figsize)
    ax=plt.subplot()
    _=ax.barh(x,y)
    max_x=max(y)
    #tick_gap=50 if max_x%1000==max_x else 100
    #_=ax.set_xticks(range(0,max_x+tick_gap,tick_gap))
    tick_gap=ax.get_xticks()[1]-ax.get_xticks()[0]
    ax.set_xlim(0,round(max_x,-1)+tick_gap/2)
    _=ax.set_yticks(range(len(x)))
    #_=ax.set_yticklabels(x, rotation = rotation,ha=ha)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    for k,v in enumerate(y):
        ax.annotate(v,(v-len(str(v))*(tick_gap/8),k-.1),color="white")

def nlp_tokenize_lower(string):
    return [token.text.lower() for token in nlp(string)]

def read_email_file(filename):
    with open(filename) as f:
        message = email.message_from_file(f)
    return message.get_payload()

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
    for line in message.split('\n'):
        # exclude forwarded information
        if ('forwarded' in line.lower() or 'original' in line.lower()) and '--' in line:
            message_count += 1
            include_text = False
        if include_text:
            words.extend(nlp_tokenize_lower(line))
    
    return {"message":words, "count": message_count, "IsPersonal": isPersonal}

def lemmatize(x):
    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in x])

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


    email_files = [f.replace('.cats', '') for f in glob.glob('./*/*/*.cats')]
    top_cnt=dict([(k,0) for k,v in id_to_top_cat.items()])
    category_freq = dict([(k,dict([(k2,0) for k2,_ in v.items()])) for k,v in id_to_sub_cat.items()])
    category_cnt = copy.deepcopy(category_freq)
    total_freq = 0
    label_freq = 0
    labeled_files = []

    for email_file in email_files:
        labels = get_labels(email_file)
        for top_cat in labels:
            top_cnt[top_cat]+=1
            for sub_cat in labels[top_cat]:
                total_freq += labels[top_cat][sub_cat]

        
            has_label = False
            for sub_cat in labels[top_cat]:
                freq = labels[top_cat][sub_cat]
                category_freq[top_cat][sub_cat] += freq
                category_cnt[top_cat][sub_cat] += 1
                label_freq += freq
                has_label = True
            if has_label:
                labeled_files.append(email_file)

    x=[id_to_top_cat[k] for k in top_cnt.keys()]

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

    message_length=np.array([len(c["message"]) for c in content])

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

    pipe_rf = Pipeline(steps = [('tf', TfidfVectorizer()), ('rf', RandomForestClassifier())])

    pgrid_rf = {
        'tf__max_features' : [1000, 2000, 3000],
        'tf__stop_words' : ['english', None],
        'tf__ngram_range' : [(1,1), (1,2)],
        'tf__use_idf' : [True, False],
    }

    gs_rf = GridSearchCV(pipe_rf, pgrid_rf,cv=10,n_jobs=-1)

    gs_rf.fit(X_train, Y_train)

    print(len(df.loc[df['preds_rf'] == 1]))

    return len(df.loc[df['preds_rf'] == 1])

main()