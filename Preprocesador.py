from nltk import word_tokenize
from nltk.stem import SnowballStemmer
import re,os,string
#Descargar las stopwords primero con el downloader de nltk
#En la consola de Anaconda, correr: python -m nltk.downloader stopwords
from nltk.corpus import stopwords

class Preprocesador(object):
    def __init__(self):
        #Importa el lematizador
        self.stemmer = SnowballStemmer('spanish')

        #Importar stopwords y quitar negaciones y palabras que indiquen cantidad
        self.spanish_stopwords = stopwords.words('spanish')
        self.spanish_stopwords.remove('no')
        self.spanish_stopwords.remove('nada')
        self.spanish_stopwords.remove('más')
        self.spanish_stopwords.remove('sin')
        self.spanish_stopwords.remove('ni')
        with open('Stopwords.txt', 'w', encoding='utf-8') as f:
            for palabra in self.spanish_stopwords:
                f.write(palabra + "\n")
                
        with open('EmoticonesPositivos.txt', 'r', encoding='utf-8') as f:
            self.emoticonesPositivos = f.read().splitlines()
                
        with open('EmoticonesNegativos.txt', 'r', encoding='utf-8') as f:
            self.emoticonesNegativos = f.read().splitlines()
            
        print(self.emoticonesPositivos[:10])
        print(self.emoticonesNegativos[:10])

    def tweetCleaner(self, text):    
        #Patrones para hacer limpiezas
        patronURL = r'https?:/?/?[A-Za-z0-9./]+'
        patronWWW = r'www.[^ ]+'
        patronNums = r'\d+'
        patronElongaciones1Char = r'(.)\1+'
        #Este último fue tomado de https://stackoverflow.com/questions/16884258/php-remove-duplicate-syllable-word
        patronElongacionesSilabas = r'([b-df-hj-np-tv-xz][aeiouy](?:[a-z])?|[aeiouy][b-df-hj-np-tv-xz](?:[a-z])?)(\1){2,}'

        #Reemplaza URLs con una "palabra" única
        clean = re.sub(patronURL, 'xurlx', text)
        clean = re.sub(patronWWW, 'xurlx', clean)
        
        #Quita caracter identificar de UTF-8 BOM si existe
        try:
            clean = clean.decode("utf-8-sig").replace(u"\ufffd", "?")
        except:
            clean = clean
        
        #Pasa todo a minúsculas
        clean = clean.lower()        
        #Reemplaza números con una "´palabra" única
        clean = re.sub(patronNums, "xnumx", clean)    
        #Reduce las elongaciones de un mismo caracter a solo 2 repeticiones
        clean = re.sub(patronElongaciones1Char, r'\1\1', clean) 
        #Reduce las elongaciones de una misma silaba a solo 2 repeticiones
        clean = re.sub(patronElongacionesSilabas, r'\1\1', clean)
        
        #Quitar stopwords
        #clean = ' '.join([word for word in clean.split() if word not in spanish_stopwords])
        
        #Reemplazar emoticones
        clean = ' '.join([word if word not in self.emoticonesPositivos else 'emopos' for word in clean.split()])
        clean = ' '.join([word if word not in self.emoticonesNegativos else 'emoneg' for word in clean.split()])
        
        #Quitar caracteres inválidos
        clean = clean.translate(str.maketrans('', '', string.punctuation)).lower()
        
        #Sacar los lemas
        #clean = ' '.join([stemmer.stem(i) for i in word_tokenize(clean)])
        
        return clean
