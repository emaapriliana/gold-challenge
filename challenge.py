#import library yang akan digunakan
import pandas as pd
import sqlite3
import function as f

from flask import Flask, jsonify, render_template

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

#membaca data.csv
data_twitter = pd.read_csv('data.csv', encoding='latin-1')

#Flask and Swagger Configuration
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
#End of Flask and Swagger Configuration

#Start ENDPOINT PERTAMA/LANDING PAGE

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
#End of ENDPOINT PERTAMA

#Start ENDPOINT KEDUA
#Route untuk menampilkan teks original dari data.csv
@swag_from("docs_challenge/text_ori.yml", methods=['GET'])
@app.route('/text-ori', methods=['GET'])
def text_ori():

    tweets_ori = []
    for tweet in data_twitter['Tweet'].items():
        tweets_ori.append(f"{tweet[1]}")#print(f"{nomor+1}. {tweet}")

    json_response = {
        'status_code': 200,
        'description': "Berikut ini adalah list dari Abusive Tweet dengan teks original sebelum dibersihkan",
        'data': tweets_ori
    }

    response_data = jsonify(json_response)
    return response_data
#End of ENDPOINT KE DUA

#Start ENDPOINT KETIGA
#Route untuk menampilkan teks tweet yang sudah dibersihkan
@swag_from("docs_challenge/text_cleansed.yml", methods=['GET'])
@app.route('/text-cleansed', methods=['GET'])

def text_cleansed():
    
    #menyimpan hasil dari teks_twit ke dalam list kosong bernama tweets_cleansed
    tweets_cleansed = [] 
    for teks_twit in data_twitter['Tweet']:   #perulangan untuk setiap teks_twit di kolom Tweet
        teks_twit = f.preprocess(teks_twit)
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
#End of ENDPOINT KE TIGA

#Start ENDPOINT KE EMPAT
#Route untuk cleansing text yang di input oleh user
@swag_from("docs_challenge/clean_text_input.yml", methods=['POST'])
@app.route('/input-text-to-clean', methods=['POST'])

def clean_text_input():
    
    if request.method == 'POST':
        teks_twit = request.form.get('text')
        teks_twit = f.preprocess(teks_twit)
           
        json_response = {
            'status_code': 200,
            'description': "Hasil dari teks yang sudah dibersihkan",
            'data': teks_twit
        }
        
        return jsonify(json_response)
#End of ENDPOINT KE EMPAT
    
#Start ENDPOINT KELIMA
#Route untuk cleansing text melalui upload file oleh user
@swag_from("docs_challenge/clean_text_file.yml", methods=['POST'])
@app.route('/input-file-to-clean', methods=['POST'])

def clean_file_input():
    
    cleaned_text_file = [] 
    file = request.files.getlist('file')[0]

    #import file csv ke pandas
    df = pd.read_csv(file, encoding='latin-1')

    for teks_twit in df['Tweet']:   #perulangan untuk setiap teks_twit di kolom Tweet
        teks_twit = f.preprocess(teks_twit)
        cleaned_text_file.append(teks_twit)

    # df = pd.DataFrame({'cleaned_text':cleaned_text})
 
    json_response = {
        'status_code': 200,
        'description': "Hasil dari teks yang sudah dibersihkan",
        'data': cleaned_text_file
    }
    
    response_data = jsonify(json_response)
    return response_data
#End of ENDPOINT KE LIMA

if __name__ == '__main__':
   app.run()

   