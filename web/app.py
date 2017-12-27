#coding:utf8

import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import re
import ast
import pandas as pd
import numpy as np
import pickle
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import load_model

maxlen=25

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

word_dict = pd.read_csv('./data/word_dict.csv', encoding='utf8')
word_dict = word_dict.drop(['0'], axis=1)
word_dict.columns = ['0', 'id']
int_catagory = load_obj('./data/int_catagory')
catagory_dict = load_obj('./data/catagory_dict')
model = load_model('./data/model.hdf5')
print "model is loaded!"

def prediction(title):
    words = re.findall('[\x80-\xff]{3}|[\w\W]', title)
    w2v = [word_dict[word_dict['0']==x]['id'].values[0] for x in words]
    xn = sequence.pad_sequences([w2v], maxlen=maxlen)
    predicted = model.predict(xn, verbose=0)[0]
    idx = predicted.argsort()[-3:]
    ret = {
        '1.category': int_catagory[idx[-1]].encode('utf8'),
        '1.possibility': str(predicted[idx[-1]]),
        '2.category': int_catagory[idx[-2]].encode('utf8'),
        '2.possibility': str(predicted[idx[-2]]),
        '3.category': int_catagory[idx[-3]].encode('utf8'),
        '3.possibility': str(predicted[idx[-3]])
    }
    return ret

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    if not request.json or not 'title' in request.json:
        abort(400)
    title = request.json['title']
    result = prediction(title)
    return jsonify({'result': result}), 200

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='127.0.0.1', debug=False)
