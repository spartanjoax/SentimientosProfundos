import math

class UnigramaModeloLenguaje(object):
    def __init__(self, oraciones):
        self.frecuenciasUnigramas = dict()
        self.diccionario = dict()
        self.diccionarioInvertido = dict()
        self.tamanoCorpus = 0
        for oracion in oraciones:
            for palabra in oracion.split(' '):
                self.frecuenciasUnigramas[palabra] = self.frecuenciasUnigramas.get(palabra, 0) + 1
                self.tamanoCorpus += 1
        dictSort = sorted(self.frecuenciasUnigramas, key=self.frecuenciasUnigramas.get, reverse=True)
        for palabra in dictSort:
            if palabra not in self.diccionario:
                self.diccionario[palabra] = len(self.diccionario)
        for k, v in self.diccionario.items():
            self.diccionarioInvertido[v] = k
        self.palabrasUnicas = len(self.frecuenciasUnigramas)

    def obtenerDiccionarioInvertido(self):
        return self.diccionarioInvertido

    def obtenerDiccionario(self):
        return self.diccionario

    def obtenerVocabularioFrecuencias(self):
        return self.frecuenciasUnigramas

    def obtenerVocabularioOrdenado(self):
        vocabularioCompleto = list(self.diccionario.keys())
        vocabularioCompleto.sort()
        return vocabularioCompleto
