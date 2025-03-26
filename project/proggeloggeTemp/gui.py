import math as m
import sys, os
from datetime import datetime

start = datetime.now()

# your code here

primes = [2]

max = int(input("max primenumber: "))
sys.stdout = open(os.devnull, 'w')  # ⛔ prints disabled

p = True

for i in range(3,max,2):
    p = True
    sqrt_i = m.isqrt(i)
    for j in primes:
        print(f"checking if {i} % {j} = 0")
        if(j>sqrt_i):
            print(f"Sqrt limit reached. Breaking")
            break
        if (i % j == 0):
            p = False
            print(f"{i} % {j} == 0. Breaking")
            break

        #Hadde det vert en god idee å ha en timer. slik at denne ifen bare ble gort etter en hvis tid?
    if p:
        primes.append(i)
        print(f"{i} is prime")


sys.stdout = sys.__stdout__         # ✅ prints back

end = datetime.now()

duration = end - start

print(f"The set of all primes in the range 0 to {max} is:")
print(primes[-1])
print(f"runtime was {duration.total_seconds():.2f} seconds")
print(f"The number of primes below {max+1} is {len(primes)}")
