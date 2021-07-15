from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import sys
#from clean_string import CleanString
from get_data_from_db import GetDataFromDB
#from jpype import getDefaultJVMPath, shutdownJVM, startJVM
import Levenshtein as lev
from similarity.ngram import NGram
import os

class Main(GetDataFromDB):

	def levenshtein(self, machined_product_cleaned_name, machined_master_product_cleaned_name):
		lev_sim = lev.ratio(machined_product_cleaned_name,machined_master_product_cleaned_name)
		return lev_sim

	def cosinus(self, machined_product_cleaned_name, machined_master_product_cleaned_name):
		values = []
		values.append(machined_product_cleaned_name)
		values.append(machined_master_product_cleaned_name)

		vectorizer =  CountVectorizer().fit_transform(values)
		vectors = vectorizer.toarray()
		cos_sim = cosine_similarity(vectors)
		return cos_sim[0][1]

	def jaccard(self, first, second):
		fcount = 0
		scount = 0
		for f in first:
			if f in second:
				scount += 1
		fcount = len(first)+len(second)
		jac_sim = float(scount) / float(fcount)
		
		return jac_sim

	def q_gram(self, machined_product_cleaned_name, machined_master_product_cleaned_name, q_gram_number=3):
		q_gram = NGram(q_gram_number)
		q_gram_sim = 1-q_gram.distance(machined_product_cleaned_name, machined_master_product_cleaned_name)

		return q_gram_sim

	def compare_cleaned_names(self, machined_products_df, machined_master_products_df):
		result_df = pd.DataFrame()
		product_counter = 0
		true_and_upper_limit_matching_counter = 0
		false_and_upper_limit_matching_counter = 0
		true_and_under_limit_matching_counter = 0
		false_and_under_limit_matching_counter = 0
		for ind1 in machined_products_df.index:
			product_counter += 1
			print(f"compared_product_count: {product_counter}")
			biggest_sim = -1
			result_dict = {}
			for ind2 in machined_master_products_df.index:
				#sim = self.cosinus(machined_products_df['cleaned_name'][ind1], machined_master_products_df['cleaned_name'][ind2])
				#sim = self.levenshtein(machined_products_df['cleaned_name'][ind1], machined_master_products_df['cleaned_name'][ind2])
				#sim = self.jaccard(machined_products_df['cleaned_name'][ind1], machined_master_products_df['cleaned_name'][ind2])
				sim = self.q_gram(machined_products_df['cleaned_name'][ind1], machined_master_products_df['cleaned_name'][ind2],6)
				if sim > biggest_sim:
					#if machined_products_df['master_product_id'][ind1] == machined_master_products_df['master_product_id'][ind2]:
					biggest_sim = sim
					result_dict['product_id'] = machined_products_df['product_id'][ind1]
					result_dict['current_master_product_id'] = machined_products_df['master_product_id'][ind1]
					result_dict['new_master_product_id'] = machined_master_products_df['master_product_id'][ind2]
					result_dict['sim'] = sim
					# ürünün sitedeki ismi
					result_dict['product_actual_name'] = machined_products_df['name'][ind1]
					# ürünü eşleşmesi gereken master product ismi
					result_dict['must_match_master_product_actual_name'] = machined_products_df['must_match_master_product_actual_name'][ind1]
					# ürünün eşleştiği master product ismi
					result_dict['matched_master_product_actual_name'] = machined_master_products_df['name'][ind2]
					# ürünün sitedeki isminin temizlenmiş hali
					result_dict['product_cleaned_name'] = machined_products_df['cleaned_name'][ind1]
					# ürünün eşleştiği master ürünün temizlenmiş hali
					result_dict['matched_master_product_cleaned_name'] = machined_master_products_df['cleaned_name'][ind2]
					
			if biggest_sim > 0.50: # benzerlik limitin üstünde ise
				if result_dict['new_master_product_id'] == result_dict['current_master_product_id']:# eşleşme doğru ve ve benzerlik limitin üstünde ise
					true_and_upper_limit_matching_counter += 1
					print(f"true_and_upper_limit_matching_counter: {true_and_upper_limit_matching_counter}")
					# insert result df
					result_dict['status'] = 1
					result_df = result_df.append(result_dict, ignore_index=True)
				else:# eşleşme yanlış ve benzerlik limitin üstünde ise
					false_and_upper_limit_matching_counter += 1
					print(f"false_and_upper_limit_matching_counter: {false_and_upper_limit_matching_counter}")
					# insert result df
					result_dict['status'] = 2
					result_df = result_df.append(result_dict, ignore_index=True)
			else: # benzerlik limitin altında ise
				if result_dict['new_master_product_id'] == result_dict['current_master_product_id']:# eşleşme doğru ve ve benzerlik limitin altında ise
					true_and_under_limit_matching_counter += 1
					print(f"true_and_under_limit_matching_counter: {true_and_under_limit_matching_counter}")
					# insert result df
					result_dict['status'] = 3
					result_df = result_df.append(result_dict, ignore_index=True)
				else:# eşleşme yanlış ve benzerlik limitin altında ise
					false_and_under_limit_matching_counter += 1
					print(f"false_and_under_limit_matching_counter: {false_and_under_limit_matching_counter}")
					# insert result df
					result_dict['status'] = 4
					result_df = result_df.append(result_dict, ignore_index=True)
					
					
		if result_df.empty:
			return "No Result Found"
		convert_dict = {'current_master_product_id': int,'new_master_product_id': int,'product_id': int,
						'product_cleaned_name': str,'matched_master_product_cleaned_name': str,'sim': float,'status':int,
						'product_actual_name':str ,'matched_master_product_actual_name':str,'must_match_master_product_actual_name':str}
		data_typed_result_df = result_df.astype(convert_dict)
		result_df = data_typed_result_df[['product_id','current_master_product_id','new_master_product_id','sim',
										'product_actual_name','must_match_master_product_actual_name','matched_master_product_actual_name',
										'product_cleaned_name','matched_master_product_cleaned_name','status']]
		return result_df

	def write_to_excel(self,df, file_name):
		writer = pd.ExcelWriter(file_name)
		df.to_excel(writer)
		writer.save()

	def change_color_group(self,x):
		color_df = x.copy()
		color_df.loc[color_df['status'] == 1, :] = 'background-color: white'
		color_df.loc[color_df['status'] == 2, :] = 'background-color: red'
		color_df.loc[color_df['status'] == 3, :] = 'background-color: blue'
		color_df.loc[color_df['status'] == 4, :] = 'background-color: yellow'
		return color_df  

	def run(self):
		# start jvm
		# ZEMBEREK_PATH = r'%s/zemberek-full.jar' % os.getcwd()
		# startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))

		# cleaned products from db
		# products_df = self.get_products_from_db()
		# clean_string = CleanString(products_df)
		# machined_products_df = clean_string.run()

		machined_products_df = pd.read_excel('cleaned_data/cleaned_products.xlsx', index_col=0)

		#self.write_to_excel(machined_products_df, "machined_products_output.xlsx")

		# cleaned master_products from excel
		machined_master_products_df = pd.read_excel('cleaned_data/cleaned_master_products.xlsx', index_col=0)

		# cleaned master_products from db
		# master_products_df = self.get_limit_master_products_from_db()
		# clean_string = CleanString(master_products_df)
		# machined_master_products_df = clean_string.run()
		
		result_df = self.compare_cleaned_names(machined_products_df, machined_master_products_df)
		print(result_df)
		colored_df = result_df.style.apply(self.change_color_group, axis=None)

		self.write_to_excel(colored_df, "result_data/qgram6_result_output.xlsx")

		# close jvm
		# shutdownJVM()

main = Main()
main.run()