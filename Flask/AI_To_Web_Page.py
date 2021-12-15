# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import re
from gensim import corpora
from gensim.models.fasttext import FastText
from konlpy.tag import Mecab
from rank_bm25 import BM25Okapi
import nmslib
import gensim
import time
import pymysql
from ftfy import fix_text, explain_unicode
from collections import Counter

from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask import Response


df = pd.read_csv('df_video_lists_morphs_id.csv',encoding='utf-8-sig')
ft_model = FastText.load('YT_fasttext.model')
with open( "weighted_doc_vects.p", "rb" ) as f:
    weighted_doc_vects = pickle.load(f)
data = np.vstack(weighted_doc_vects)



app = Flask(__name__)
@app.route('/predict')

def predict_code():
    keyword_list = []
    parameter_dict = request.args.to_dict()
    if len(parameter_dict) == 0:
        return 'No parameter'

    parameters = ''
    for key in parameter_dict.keys():
        #parameters += 'key: {}, value: {}\n'.format(key, request.args[key])
        keyword_list.append(request.args[key])
    return model_predict(keyword_list)



def model_predict(keyword_list):
    
    
    #input_keyword = []
    index = nmslib.init(method='hnsw', space='cosinesimil')
    index.loadIndex('Hifen_video_fasttext_index')
        
    #print(len(input_keyword))
            
    counter = Counter()
    query = [ft_model.wv.get_vector(vec) for vec in keyword_list]
    query = np.mean(query,axis=0)
    
    #print(query)

    t0 = time.time()
    
    ids, distances = index.knnQuery(query, k=100)
    t1 = time.time()
    for i,j in zip(ids,distances):
        counter[df.channel_id.values[i]] +=1    
    
    return dict(counter.most_common())

#@app.route('/index')
#def index():
#    return 'Hello Flask!'
