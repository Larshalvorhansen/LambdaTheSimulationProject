import random

class Grass:
    i = 0
    def __init__(self, length=3, height=None):
        Grass.i += 1
        self.length = length
        self.height = height if height is not None else random.random()
        self.id = f"grass{self.i}"

    def printer(self):
        print(f"Id: {self.id} Length: {self.length}, Heigth: {self.height}")

allGrass = {}

for i in range(10):
    allGrass[f'straw{i}'] = Grass()

for i in range(10):
    allGrass[i].printer()

# variables = {}
# for i in range(10):
#     variables[f'var{i}'] = i

# print("Dictionary method:")
# print(variables)

# # Using exec
# print("\nExec method:")
# for i in range(10):
#     exec(f'var{i} = {i}')

# print(var0)
# print(var1)
# print(var2)