#import library yang akan digunakan
import pandas as pd
import re

#Membaca data knowledge base
data_kamusalay = pd.read_csv('new_kamusalay.csv', encoding='latin-1', header=None)
data_kamusalay = data_kamusalay.rename (columns = {0: 'before', 1: 'after'})
data_abusive = pd.read_csv('abusive.csv', header=None)
kamus_alay = dict(zip(data_kamusalay['before'], data_kamusalay['after']))

#fungsi untuk mengubah seluruh karakter menjadi huruf kecil (lowercase)
def lowercase(teks_twit):
        return teks_twit.lower()

#fungsi menghapus/mengganti karakter yang tidak perlu
def remove_unnecessary_char(teks_twit):
        
    #step 1, hilangkan teks yang berawalan dari http sampai habis kalimat atau sampai first space
    teks_twit = re.sub(r'(http[^\s]+)', r'', teks_twit) 
    #step 2, menghapus \xDD substring 
    teks_twit = re.sub (r'(?:\\x[A-Fa-f0-9]{2})+', r'', teks_twit)
    #step 3, menghapus spesifik kata user
    teks_twit = re.sub(r'\buser\b', r'', teks_twit)
    #step 4, menghapus spesifik kata rt
    teks_twit = re.sub(r'\brt\b', r'', teks_twit)
    #step 5, menghapus \n
    teks_twit = re.sub(r"\\n",' ', teks_twit)
    #step 6, menghapus non alfanumerik karakter
    teks_twit = re.sub(r"[^A-Za-z0-9\s]+", ' ', teks_twit)
    #step 7, menghapus spesifik kata url
    teks_twit = re.sub(r'\burl\b', r'', teks_twit)
    #step 8, me-replace 2 atau lebih whitespace menjadi single space
    teks_twit = re.sub(r'\s{2,}', ' ', teks_twit) 
    #step 9, menghilangkan whitespace di awal dan di akhir teks_twit
    teks_twit = teks_twit.strip()

    return teks_twit
    
#fungsi untuk mengubah kata alay menjadi kata yang lebih baku menurut file new_kamusalay.csv
def normalize_alay_word(teks_twit):
    return ' '.join([kamus_alay[kata] if kata in kamus_alay 
                                            else kata for kata in teks_twit.split(' ')])

#fungsi mengganti kata abusive yang ada di teks_twit dengan XXXXX. 
# kata yang dianggap abusive adalah kata-kata yang ada di file abusive.csv
def replace_abusive_word(teks_twit):
    kamus_abusive = '|'.join(list(data_abusive[0]))
    teks_twit = re.sub(kamus_abusive, r'XXXXX', teks_twit)

    return teks_twit

#fungsi untuk menggabungkan seluruh fungsi cleansing menjadi 1 fungsi bernama preprocess
def preprocess(teks_twit):
    teks_twit = lowercase(teks_twit)
    teks_twit = remove_unnecessary_char(teks_twit)
    teks_twit = normalize_alay_word(teks_twit)
    teks_twit = replace_abusive_word(teks_twit)
    return teks_twit