import csv

def convertToArray(csvFile):
    with open(f"relationalDatabase/commoditiesData/{csvFile}.csv", newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        myArray = []
        for row in csvreader:
            myArray.append(row)
        return myArray
def convertFromArrayWithToupleToList(array):
    newArray
    for i in array:
        pass
    return newArray
def averageArray(array):
    sum = 0
    for i in array:
        sum += float(i[1])
    return sum / len(array)
def main():
    #allComm = convertToArray("allCommodities")
    #print(averageArray(allComm))
    print("test")
    
if __name__ == "__main__":
    main()
