def jaccard (first, second):
    fcount = 0 
    scount = 0
    for f in first:
        if f in second:
            scount += 1
    fcount = len(first)+len(second)
    
    score = float(scount) / float(fcount)
    print(fcount)
    print(scount)
    return score

result = jaccard('doğal dil işleme','işleme dil doğal')
print(result)