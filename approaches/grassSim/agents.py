import random as r

class Grass:
    length = 0
    pos = (0,0)
    growthFactor = r.randint(1,10)
    spreadFactor = r.randint(1,10)

class Weed:
    length = 0
    pos = (0,0)
    growthFactor = r.randint(1,10)
    spreadFactor = r.randint(1,10)

def growBy1Day(listOfInstances):
    for g in listOfInstances:
        grow = g.growthFactor
        g.length += grow

def printGrass(listOfInstances):
    for g in listOfInstances:
        print(f"{g.length}, ", end ="")

AllGrass = []

for i in range(10):
    AllGrass.append(Grass)

numberOfDays = 10

printGrass(AllGrass)

for g in AllGrass:
    growBy1Day(AllGrass)

printGrass(AllGrass)