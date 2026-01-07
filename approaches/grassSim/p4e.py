import ast

pyFile = "agents2.py"
newFilePath = "data/"

def py2ast(pyFile):
    return ast.parse(pyFile)

def ast2c(_ast):
    return 0

def main():
    print(ast.dump(py2ast(pyFile),indent = 4))


if __name__ == '__main__':
    main()