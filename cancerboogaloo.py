g=[[1,2,3],[4,5,6],[7,8,9],[10,11,12]]


def setupdata(explanatory):
    length = range(len(explanatory[0]))
    data = [[] for i in length]
    counter = 0
    subcounter = 0
    for number in length:
        for element in explanatory[:-1]:
            data[counter].append(element[subcounter])
        subcounter += 1
        counter += 1
    return data

print(setupdata(g))
