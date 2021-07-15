from similarity.ngram import NGram

s1 = 'hasan deli'
s2 = 'basan feli'
fourgram = NGram(2)
print(1-fourgram.distance(s1, s2))