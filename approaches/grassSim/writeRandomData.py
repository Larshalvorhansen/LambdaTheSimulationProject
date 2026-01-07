import random as r

def writeRandom():
    for i in range(5):
        k = (f"data/data{i}.csv")
        f = open(k,"w")
        f.write(f"i, random1, random2, random3\n")
        for i in range(100):
            f.write(f"{i}, {r.random()}, {r.random()}, {r.random()}\n")
        f.close()

writeRandom()