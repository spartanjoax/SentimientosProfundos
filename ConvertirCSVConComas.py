import os

archivoOrigen = "datosTassLimpiosConIdAgreementPolaridadYTexto.csv"
archivoDestino = "tweets.csv"

def procesar(line):
    contador = 0
    try:
        palabras = line.split()
        line = ""
        for palabra in palabras:
            if palabra != "":
                contador += 1
                if contador <= 3:
                    line += palabra + ","
                else:
                    line += palabra + " "
        line = line[:-1]
    except Exception as inst:
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst           # __str__ allows args to be printed directly
    return line

if os.path.isfile(archivoDestino):
    os.remove(archivoDestino)

with open(archivoOrigen) as f:
    lines = f.read().splitlines()
    for line in lines:
        line = procesar(line)
        with open(archivoDestino, 'a') as f:
            f.write(line + '\n')