import re
import pandas as pd
import sqlite3
import gradio as gr

from flask import Flask, jsonify, render_template

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

data_twitter = pd.read_csv('data.csv', encoding='latin-1')
data_kamusalay = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
data_kamusalay = data_kamusalay.rename (columns = {0: 'before', 1: 'after'})
data_abusive = pd.read_csv('abusive.csv', header=None)
kamus_alay = dict(zip(data_kamusalay['before'], data_kamusalay['after']))

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
    
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


# ENDPOINT PERTAMA/LANDING PAGE

@swag_from("docs_challenge/introduction.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def introduction():
    
    json_response = {
        'status_code': 200,
        'description': "Ini adalah halaman utama pada API Data Cleansing (Rahmatina Ari Apriliana)",
        'data': [
        
        "- http://127.0.0.1:5000/text-ori , Untuk melihat teks original dari data Abusive tweet", 
        "- http://127.0.0.1:5000/text-cleansed , Untuk melihat hasil cleansing teks original dari data Abusive tweet",
        "- http://127.0.0.1:5000/input-text-to-clean , Untuk membersihkan teks yang di-input oleh user",
        "- http://127.0.0.1:5000/input-file-to-clean , Untuk membersihkan file yang berisi teks, yang di-input oleh user"

        
        ]
    }

    

    response_data = jsonify(json_response)
    return response_data

#ENDPOINT KEDUA

@swag_from("docs_challenge/text_ori.yml", methods=['GET'])
@app.route('/text-ori', methods=['GET'])
def text_ori():

    
    tweets_ori = []
    for tweet in data_twitter['Tweet'].items():
        tweets_ori.append(f"{tweet[1]}")#print(f"{nomor+1}. {tweet}")

    # #Membuat dataframe dari tweets_ori
    # df = pd.DataFrame({'original_tweet': tweets_ori})

    # #menyimpan dataframe ke dalam sqlite database

    # conn = sqlite3.connect('challenge.db')
    # df.to_sql('tweet_original', conn, if_exists='replace')
    # conn.close()


    json_response = {
        'status_code': 200,
        'description': "Berikut ini adalah list dari Abusive Tweet dengan teks original sebelum dibersihkan",
        'data': tweets_ori
    }

    

    response_data = jsonify(json_response)
    return response_data

# data_kamusalay = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
# data_kamusalay = data_kamusalay.rename (columns = {0: 'before', 1: 'after'})
# data_twitter = pd.read_csv('data.csv', encoding='latin-1')
# kamus_alay = dict(zip(data_kamusalay['before'], data_kamusalay['after']))
# data_abusive = pd.read_csv('abusive.csv', header=None)

# ENDPOINT KETIGA

@swag_from("docs_challenge/text_cleansed.yml", methods=['GET'])
@app.route('/text-cleansed', methods=['GET'])

def text_cleansed():
    #fungsi cleansing 1, mengubah seluruh teks_twit menjadi karakter lowercase (huruf kecil)
    def lowercase(teks_twit):
        return teks_twit.lower()

    #fungsi cleansing 2, menghapus/mengganti karakter yang tidak perlu
    def remove_unnecessary_char(teks_twit):
        
        #step 1, hilangkan teks yang berawalan dari http sampai habis kalimat atau sampai first space
        teks_twit = re.sub(r'(http[^\s]+)', r'', teks_twit) 
        #step 2, remove \xDD substring 
        teks_twit = re.sub (r'(?:\\x[A-Fa-f0-9]{2})+', r'', teks_twit)
        #step 3, remove spesifik kata user
        teks_twit = re.sub(r'\buser\b', r'', teks_twit)
        #step 4, remove spesifik kata rt
        teks_twit = re.sub(r'\brt\b', r'', teks_twit)
        #step 5, remove \n
        teks_twit = re.sub(r"\\n",' ', teks_twit)
        #step 6, remove non alfanumerik karakter
        teks_twit = re.sub(r"[^A-Za-z0-9\s]+", ' ', teks_twit)
        #step 7, remove spesifik kata url
        teks_twit = re.sub(r'\burl\b', r'', teks_twit)
        #step 8, me-replace 2 atau lebih whitespace menjadi single space
        teks_twit = re.sub(r'\s{2,}', ' ', teks_twit) 
        #step 9, menghilangkan whitespace di awal dan di akhir teks_twit
        teks_twit = teks_twit.strip()

        return teks_twit
    
    #fungsi cleansing 3, mengubah kata alay menjadi kata yang lebih baku menurut file new_kamusalay.csv
    def normalize_alay_word(teks_twit):
        return ' '.join([kamus_alay[kata] if kata in kamus_alay 
                                                else kata for kata in teks_twit.split(' ')])
    
    #fungsi cleansing 4, mengganti kata abusive yang ada di teks_twit dengan XXXXX. kata yang dianggap abusive adalah kata-kata yang ada di file abusive.csv
    def replace_abusive_word(teks_twit):
        kamus_abusive = '|'.join(list(data_abusive[0]))
        teks_twit = re.sub(kamus_abusive, r'XXXXX', teks_twit)

        return teks_twit

    #menggabungkan seluruh fungsi cleansing menjadi 1 fungsi bernama preprocess
    def preprocess(teks_twit):
        teks_twit = lowercase(teks_twit)
        teks_twit = remove_unnecessary_char(teks_twit)
        teks_twit = normalize_alay_word(teks_twit)
        teks_twit = replace_abusive_word(teks_twit)
        return teks_twit
    
    #menyimpan hasil dari teks_twit ke dalam list kosong bernama tweets_cleansed
    tweets_cleansed = [] 
    for teks_twit in data_twitter['Tweet']:   #perulangan untuk setiap teks_twit di kolom Tweet
        teks_twit = preprocess(teks_twit)
        tweets_cleansed.append(teks_twit)

    #Membuat dataframe dari tweets_ori dan teks_twit
    #data_twitter['Tweet'] adalah tweet ori yang disimpan dalam kolom original_tweet, dan tweets_cleansed disimpan dalam kolom cleaned_twit
    df = pd.DataFrame({'original_tweet': data_twitter['Tweet'], 'cleaned_tweet': tweets_cleansed})

    #menyimpan dataframe ke dalam sqlite database dengan nama challenge.db
    conn = sqlite3.connect('challenge.db')
    df.to_sql('tweet', conn, if_exists='replace', index_label='index')
    conn.close()   

    json_response = {
        'status_code': 200,
        'description': "Berikut ini adalah list dari Abusive Tweet dengan teks yang sudah dibersihkan",
        'data': tweets_cleansed
         }

    response_data = jsonify(json_response)
    return response_data



#ENDPOINT KEEMPAT
#Route untuk cleansing text input from user
@swag_from("docs_challenge/clean_text_input.yml", methods=['POST'])
@app.route('/input-text-to-clean', methods=['POST'])

def clean_text_input():
    #step 1, mengubah semua karakter menjadi huruf kecil(lowercase)
    def lowercase(text):
        return text.lower()

    def remove_unnecessary_char(text):
        #step 2, hilangkan teks yang berawalan dari http sampai habis kalimat atau sampai first space
        text = re.sub(r'(http[^\s]+)', r'', text) 

        #step 3, remove non alfanumerik karakter/ punctuation
        text = re.sub(r"[^A-Za-z0-9\s]+", '', text)

        #step 4, me-replace 2 atau lebih whitespace menjadi single space
        text = re.sub(r'\s{2,}', ' ', text) 
        
        #step 5, menghilangkan whitespace di awal dan di akhir teks_twit
        text = text.strip()

        return text
    
    def preprocess(text): #menggabungkan 2 fungsi menjadi 1 fungsi
        text = lowercase(text)
        text = remove_unnecessary_char(text)
        return text
    
    
    if request.method == 'POST':
        text = request.form.get('text')
        text = preprocess(text)
           
        json_response = {
            'status_code': 200,
            'description': "Hasil dari teks yang sudah dibersihkan",
            'data': text
        }
        
        return jsonify(json_response)
    
#ENDPOINT KELIMA
"""
REVIEW: fungsi processing_file gausah dibuat, jadi duplikat nantinya mending variable file & df di asign ke fungsi clean_file_input aja
"""
#Route untuk cleansing text dari file input user
@swag_from("docs_challenge/clean_text_file.yml", methods=['POST'])
@app.route('/input-file-to-clean', methods=['POST'])
# def processing_file():
#     #upload file
#     file = request.files.getlist('file')[0]

#     #import file csv ke pandas
#     df = pd.read_csv(file, encoding='latin-1')

#     #Mengambil teks yang akan diproses ke dalam format list
#     #texts = df.text.to_list()
#     return df

def clean_file_input():
    #step 1, mengubah semua karakter menjadi huruf kecil(lowercase)
    def lowercase(text):
        return text.lower()

    def remove_unnecessary_char(text):
        #step 2, hilangkan teks yang berawalan dari http sampai habis kalimat atau sampai first space
        text = re.sub(r'(http[^\s]+)', r'', text) 

        #step 3, remove non alfanumerik karakter/ punctuation
        text = re.sub(r"[^A-Za-z0-9\s]+", '', text)

        #step 4, me-replace 2 atau lebih whitespace menjadi single space
        text = re.sub(r'\s{2,}', ' ', text) 
        
        #step 5, menghilangkan whitespace di awal dan di akhir teks_twit
        text = text.strip()

        # tambahin cleansing rules nya sampai pembersihan step-9 kaya diatas

        return text
    
    def preprocess(text): #menggabungkan 2 fungsi menjadi 1 fungsi
        text = lowercase(text)
        text = remove_unnecessary_char(text)

        return text
    
    cleaned_text = [] 
    file = request.files.getlist('file')[0]

    #import file csv ke pandas
    df = pd.read_csv(file, encoding='latin-1')

    for text in df['Tweet']:   #perulangan untuk setiap teks_twit di kolom Tweet
        texts = preprocess(text)
        cleaned_text.append(texts)

    
    # if request.method == 'POST':
    #     text = request.form.get('text')
    #     text = preprocess(text)
           
    json_response = {
        'status_code': 200,
        'description': "Hasil dari teks yang sudah dibersihkan",
        'data': cleaned_text
    }
    
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
   app.run()


# if __name__ == '__main__':
#     app.run(debug=True)
   