import io
import math
import matplotlib.pyplot as plt
import ast

def checkIfPrime(N):
    max = round(math.sqrt(N)+1)
    """int -> Bool"""
    for i in range(3,max,2):
        if N%i==0:
            return(False)
            break
    return(True)

def checkIfSquareNumber(N):
    """int -> bool"""
    if math.sqrt(N)%1==0:
        return(True)
    else: return(False)

def computeMean(n):
    """"""
    sum = 0
    c = 0
    for i in n:
        sum+=i
        c+=1
    return(sum/c)

def plot(x, y):
    """list, list -> plot"""
    figfdsf, data = plt.subplots()
    data.plot(y)
    data.plot(x)
    plt.show()

def csvToList(csvFile):
    """csvFile -> Lists"""
    f = open(csvFile, "r")
    varz = []
    for line in f:
        n = len(line.split(", "))
        for i in range(n):
            varz.append(line.split(", ")[i])
    return varz
 
print(csvToList('data/data2.csv'))