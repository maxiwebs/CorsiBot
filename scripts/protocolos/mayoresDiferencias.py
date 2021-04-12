import numpy as np
import itertools
import ast

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
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

#Me indica cuántas letras de la seq1 estan en la seq2
def cantLetrasDeSeq1EnSeq2(seq1,seq2):
    letters = list(seq1)

    cantLetras = 0
    for letter in letters:
        apariciones = (str(seq2)).count(letter)
        #Si la letra aparece alguna vez, incremento
        if apariciones > 0:
            cantLetras+=1

    return cantLetras

#Me indica cuantasletras de seq2 no tenian que estar
def letrasDeMas(seq1,seq2):
    letters = list(str(seq2))

    letrasSobrantes = 0

    for letter in letters:
        if not(letter in list(seq1)):
            letrasSobrantes += 1

    return letrasSobrantes

#Me indican cuantas letras de seq1 estan repetidas en seq2
def cantRepetidos(seq1,seq2):
    letters = list(seq1)
    repeticiones = 0

    for letter in letters:
        apariciones = (str(seq2)).count(letter)
        if apariciones > 1:
            repeticiones+=apariciones

    return repeticiones

def levenshteinExtendido(seq1,seq2):
    letrasSobrantes = 0
    repeticiones = 0

    #Esta resta da 0 si en seq2 estan todas las letras de seq1
    repeticiones = cantRepetidos(seq1,seq2)*2

    letrasSobrantes = letrasDeMas(seq1,seq2)*3

    #Devuelvo la distancia de Lev+la penalizacion por repeticiones y letras que no estaban.
    return levenshtein(str(seq1),str(seq2))+repeticiones+letrasSobrantes


#Me duevuelve True si están las mismas letras en seq1 que en seq2 (con distinto orden, o no)
def esErrorDeCamino(trial,rta):
    return ((len(trial)-cantLetrasDeSeq1EnSeq2(trial,rta)) == 0)

#Me retorna el primer indice donde se diferencian el trial y la rta, si son iguales, devuelve -1
def indicePrimerError(trial,rta):
    if "rta" == "":
        return 0
        
    return next((i for i in range(min(len(trial), len(rta))) if trial[i]!=rta[i]), -1)

#Me da el indice del último error comenzando a comparar desde atras. Si son iguales, devuelve -1
def indiceUltimoError(trial,rta):

    size = min(len(trial),len(rta))
    result = -1

    for i in range(size):
        if trial[size-i-1] != rta[size-i-1]:
            result = i
            break

    return result

