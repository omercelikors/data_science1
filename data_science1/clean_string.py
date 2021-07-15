from jpype import JClass, JString, java, getDefaultJVMPath, shutdownJVM, startJVM
import string
import nltk
nltk.download('stopwords')
nltk.download('words')
nltk.download('wordnet')
from nltk.corpus import stopwords, words
#from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from get_data_from_db import GetDataFromDB
import pandas as pd
import os
import re

class CleanString():
	# Aşağıdaki kelimleri empty string yapıyoruz. Çünkü 40 adet ve 40'lı aynı şeydir. lı eki çeıktıktan sonra diğer tarfta adet kalacak ve eşleşmeyi olumsuz etkileyecek.
	our_specific_word = ("miktar","adet","gr","g","ml","l","lt","ekonomik","gb","cc","kg","cm","m",
						"metre","kampanya","fırsat","inç","ton","lb","küp","metreküp","kw","kulaç","m³","cm³",
						"santimetreküp","litre","gram","mililitre","santilitre","santimetre","gigabayt","kilogram",
						"fit","feet","ons","derece","libre","galon","desimetre","sayfa","yaprak","ad","yp","tl")

	
	
	def __init__(self, df):
		ZEMBEREK_PATH = r'%s/zemberek-full.jar' % os.getcwd()
		startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))
		self.df = df
		# zemberek
		self.TurkishMorphology: JClass = JClass('zemberek.morphology.TurkishMorphology')
		self.TurkishSentenceNormalizer: JClass = JClass('zemberek.normalization.TurkishSentenceNormalizer')
		self.WordAnalysis: JClass = JClass('zemberek.morphology.analysis.WordAnalysis')
		self.Paths: JClass = JClass('java.nio.file.Paths')
		# foreign nltp
		self.english_words = set(words.words())
		self.turkish_stopwords = set(stopwords.words('turkish'))
		self.english_stopwords = set(stopwords.words('english'))
		#self.english_stemmer = PorterStemmer()
		self.english_lemmatizer = WordNetLemmatizer()
		
		
	def noisy_text_normalization(self,word):
		"""
		Noisy word normalization example.
		Args:
			word (str): Noisy text to normalize.
		"""
		normalizer = self.TurkishSentenceNormalizer(
			self.TurkishMorphology.createWithDefaults(),
			self.Paths.get(f"{os.getcwd()}/zemberek_data/normalization"),
			self.Paths.get(f"{os.getcwd()}/zemberek_data/lm/lm.2gram.slm"),
		)
		return normalizer.normalize(JString(word))
	
	def get_zemberek_word_root(self,word):
		"""
		Stemming or lemmatization.
		Args:
			word (str): Word to apply stemming or lemmatization.
		"""
		morphology: self.TurkishMorphology = self.TurkishMorphology.createWithDefaults()
	
		results: self.WordAnalysis = morphology.analyzeAndDisambiguate(word).bestAnalysis()

		for analysis in results:
			if analysis.getLemmas()[0] == "UNK":
				print(f"unknown by zemberek {word}")
				return word
			else:
				return analysis.getLemmas()[0]

	def replace_our_specific_word_to_none(self,word):
		""" 64GB gibi kelimelerden "GB" ibaresini alır. """
		for spec_word in self.our_specific_word:
			
			match = re.findall('\d%s' % spec_word, str(word))
			
			if match:
				word = re.sub("[a-zA-Z]", "", word)

		return word

	def clean_sentence(self,sentence):
		last_sentence = ""
		for word in sentence.split():

			word = word.lower()

			word = ''.join([chracter for chracter in word if chracter not in string.punctuation])

			if word is None or word == '':
				continue

			if word in self.our_specific_word:
				continue
			
			word = self.replace_our_specific_word_to_none(word)

			if word in self.english_words:# nltk
				if word in self.english_stopwords:
					continue
				print(f"english {word}")
				#word = self.english_stemmer.stem(str(word))
				word = self.english_lemmatizer.lemmatize(str(word), pos = "n")
			else:# zemberek
				if word in self.turkish_stopwords:
					continue
				word = self.noisy_text_normalization(word)
				word = self.get_zemberek_word_root(word)
			
			last_sentence += f" {word}"
		return last_sentence

	def run(self):
		cleaned_name = []
		count = 0
		for ind in self.df.index:
			cleaned_sentence = self.clean_sentence(self.df['name'][ind])
			cleaned_name.append(cleaned_sentence)
			count += 1
			if count % 10 == 0:
				print(f"cleaned_product_count : {count}")
		self.df['cleaned_name'] = cleaned_name
		
		shutdownJVM()
		return self.df

#raw_products_df = pd.read_excel('test_raw_data.xlsx', index_col=0)
get_data_from_db = GetDataFromDB()
result = get_data_from_db.get_specific_products_and_master_products_from_db()

clean_string = CleanString(result[1])
last_df = clean_string.run()

# close jvm

#print(last_df)
# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('cleaned_data/cleaned_master_products.xlsx', engine='xlsxwriter')

# # Convert the dataframe to an XlsxWriter Excel object.
last_df.to_excel(writer)

# # Close the Pandas Excel writer and output the Excel file.
writer.save()


