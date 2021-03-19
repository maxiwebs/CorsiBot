import numpy as np
import itertools
import trials_raw

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in xrange(size_x):
        matrix [x, 0] = x
    for y in xrange(size_y):
        matrix [0, y] = y

    for x in xrange(1, size_x):
        for y in xrange(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    #print (matrix)
    return (matrix[size_x - 1, size_y - 1])

#Le asigna un punto a cada letra solo la primera vez que aparece
def cantLetras(seq1,seq2):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    cantLetras = 0
    for letter in letters:
        apariciones = (str(seq1+seq2)).count(letter)
        #Si la letra aparece alguna vez, incremento
        if apariciones > 0:
            cantLetras+=1

    return cantLetras

#Genero una funcion que para un conjunto de secuencias me devuelva las dos que tienen mayor distancia
def dameDosMejoresSecuencias(secs):
    mayorDistancia = 0
    secsElegidas = []
    for seq in itertools.combinations(secs,2):
        distanciaEntreEstasDosSecs = levenshtein(seq[0],seq[1]) + cantLetras(seq[0],seq[1])
        print (seq,distanciaEntreEstasDosSecs, trials_raw.intersections(seq[0])[0],trials_raw.intersections(seq[1])[0])
        if distanciaEntreEstasDosSecs > mayorDistancia:
            secsElegidas = seq
            mayorDistancia = distanciaEntreEstasDosSecs

    return secsElegidas
