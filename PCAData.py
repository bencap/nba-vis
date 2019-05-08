# CS251 - Project 6 - PCAData.py - Max Perrello - 4/10/19

import csv
import numpy as np
import sys
import pdb # pdb.set_trace()
# from data import Data
import data

class PCAData(data.Data):
	def __init__(self, projected_data, eigenvectors, eigenvalues, original_means, original_headers):
		data.Data.__init__(self, filename = None)
		self.original_headers = original_headers
		self.eigenvectors = eigenvectors # (numpy matrix)
		self.eigenvalues = eigenvalues # (numpy matrix)
		self.mean_data_values = original_means # (numpy matrix)
		self.data = projected_data
		for i in range( self.get_num_points() ):
			header_name = "PCA" + "{:02d}".format(i)
			self.headers.append(header_name)
			self.header2col[self.headers[i]] = i
		self.types = ["numeric"]*self.get_num_dimensions()

	# get_eigenvalues - returns a copy of the eigenvalues as a single-row numpy matrix
	def get_eigenvalues(self):
		# print("Eigenvalues: ", np.copy(self.eigenvalues))
		return np.copy(self.eigenvalues)

	# get_eigenvectors() - returns a copy of the eigenvectors as a numpy matrix with the eigenvectors as rows
	def get_eigenvectors(self):
		return np.copy(self.eigenvectors)

	# get_original_means() - returns the means for each column in the original 
	# data as a single row numpy matrix **ADDED OPTION TO CHOOSE HEADERS**
	def get_original_means(self):
		return self.mean_data_values

	# get_original_headers() - returns a copy of the list of the headers from the
	# original data used to generate the projected data
	def get_original_headers(self):
		return self.original_headers[:]