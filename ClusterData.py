# CS251 - Project 7 - ClusterData.py - Max Perrello - 5/1/19

import csv
import numpy as np
import sys
import pdb # pdb.set_trace()
# from data import Data
import data

class ClusterData(data.Data):
	def __init__(self, means, codes, errors, K, dataO, headers):
		data.Data.__init__(self, filename = None)
		self.means = means
		self.codes = codes
		self.errors = errors
		self.K = K
		self.data = dataO.get_data()
		self.dataObject = data
		self.headers = headers
		self.header2ColEr(self.headers) # builds self.header2col dict
		

	# get_means - returns a copy of the means
	def get_means(self):
		print("Getting Means: ", np.copy(self.means))
		return np.copy(self.means)

	# get_codes() - returns a copy of codes
	def get_codes(self):
		print("Getting codes: ", np.copy(self.codes))
		return np.copy(self.codes)

	# get_errors() - returns a copy of K
	def get_errors(self):
		print("Getting errors: ", np.copy(self.errors))
		return np.copy(self.errors)

	# get_k() - returns a copy of K
	def get_k(self):
		print("Getting K: ", np.copy(self.K))
		return np.copy(self.K)

def main(argv):
	test = ClusterData()