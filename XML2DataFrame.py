import xml.etree.ElementTree as ET
import pandas as pd

#Basado en http://gokhanatil.com/2017/11/python-for-data-science-importing-xml-to-pandas-dataframe.html
class XML2DataFrame:

    def __init__(self, xml_data):
        self.xml_data = xml_data

    def getvalueofnode(self, node):
        """ return node text or None """
        return node.text if node is not None else None

    def process_data(self):
        #Definir el nombre de las columnas del archivo
        cols = ['id','usuario','Texto','Fecha','Idioma','Polaridad']
        df = pd.DataFrame(columns=cols)

        #Cargar el xml y convertirlo a un DataFrame
        etree = ET.parse(self.xml_data) #create an ElementTree object 
        for node in etree.getroot():
                tweetId = node.find('tweetid')
                user = node.find('user')
                content = node.find('content')
                date = node.find('date')
                lang = node.find('lang')
                polarity = node.find('sentiment/polarity/value')

                df = df.append(
                    pd.Series([self.getvalueofnode(tweetId), self.getvalueofnode(user), self.getvalueofnode(content),
                               self.getvalueofnode(date), self.getvalueofnode(lang), self.getvalueofnode(polarity)], 
                              index=cols), ignore_index=True)

        return df