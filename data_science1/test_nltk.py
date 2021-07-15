import nltk
nltk.download('stopwords')
nltk.download('words')
#nltk.download('wordnet')
from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer
#from nltk.stem import WordNetLemmatizer

v = "ilgileniyorum"

# english_words = set(words.words())
# if v in english_words:
# 	print(True)
# else:
# 	print(False)


english_stemmer = PorterStemmer()
print(english_stemmer.stem(v))