function ruleToBinary(ruleNumber)
    binaryRule = zeros(Bool, 8)
    for i in 1:8
        binaryRule[i] = ((ruleNumber >> (i - 1)) & 1) == 1
    end
    return reverse(binaryRule)
end

function applyRule(grid, ruleBinary)
    newGrid = copy(grid)
    for i in 2:length(grid)-1
        neighborhood = (grid[i-1] << 2) + (grid[i] << 1) + grid[i+1]
        newGrid[i] = ruleBinary[neighborhood + 1]
    end
    return newGrid
end

function generateCA(ruleNumber, generations, width)
    ruleBinary = ruleToBinary(ruleNumber)
    grid = zeros(Bool, width)
    grid[Int(ceil(width / 2))] = true
    
    for gen in 1:generations
        # Convert grid to a string of "#" and " " and print it
        printGrid = [grid[i] ? "#" : " " for i in 1:length(grid)]
        println(join(printGrid, ""))
        grid = applyRule(grid, ruleBinary)
    end
end

# # Example usage: Rule 30 for 15 generations with a width of 31 cells
# for i in range(1,20)
#     println(i)
#     generateCA(i, 40, 50)
# end

generateCA(31, 40, 50)