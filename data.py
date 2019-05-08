# CS251 - Project 2 - data.py - Max Perrello - 3/8/19

import csv
import numpy as np
import sys

class Data:
	def __init__(self, filename = None):
		# create and initialize fields for the class
		self.csv_reader = None
		self.csvfile = None
		self.headers = [] # list of all headers (prev [])
		self.types = [] # list of all types
		self.rows = [] # list of rows of data (sublists)
		self.data = None # numPy matrix (prev None)
		self.header2col = {} # dict of headers and their column numbers
		self.nonNumericHeaders = [] # list of non-numeric columns (by header)
		self.nonNumericTypes = [] # list of non-numeric column types
		self.isNumeric = [] # true or false values for if something is numeric
		self.nonNumericRows = [] # storage of non-num rows
		if filename != None:
			self.read(filename)

	def read(self, filename): # reads in and parses data from a csv file
		with open(filename, 'rU') as self.csvfile:
			self.csv_reader = csv.reader( self.csvfile ) # python-interactable csv file object
			self.headers = self.stripper( next(self.csv_reader) )
			self.types = self.stripper( next(self.csv_reader) ) # list of all types (second line)
			tempHeadList = [] # temp holding list for numeric headers
			tempTypeList = [] # temp holding list for numeric types
			for x in range(len(self.types)): # looking for non-numeric columns
				if self.types[x] == "numeric":
					tempHeadList.append(self.headers[x]) # record numeric column
					tempTypeList.append(self.types[x]) # record numeric column
					self.isNumeric.append(True) # record whether is numeric
				else:
					self.nonNumericHeaders.append(self.headers[x]) # record non-num head
					self.nonNumericTypes.append(self.types[x]) # record non-num type
					self.isNumeric.append(False) # record whether is numeric
			self.headers = self.header2ColEr( tempHeadList )[:] # update new head global
			self.types = tempTypeList[:] # update new type global
			for row in self.csv_reader: # iterate over file object by row
				sublist = []
				nonNumericSublist = []
				for i in range(len(row)):
					if self.isNumeric[i]:
						sublist.append( float(row[i]) ) # parse each data string as float
					else:
						nonNumericSublist.append( row[i] ) # parse each data string as float
				self.rows.append(sublist) # append row to list of rows
				self.nonNumericRows.append(nonNumericSublist) # append sub to nonNumRows
		self.data = np.matrix(self.rows) # build numPy matrix from list of rows

	def stripper(self, glist): # strips whitespaces from items in given list and returns it
		newList = []
		for value in range(len(glist)):
			newList.append( glist[value].strip() ) # strip leading and trailing whitespace from each value
		return newList # return finished list

	def header2ColEr(self, list): # creates dict of headers and their columns from list
		num = 0 # counter for columns
		for item in list:
			self.header2col[item] = num # add item name as dict entry w col num as value
			num = num + 1 # increment column number
		return list # return finished list

	def floatEr(self, string): # tries to parse a string as a float, returns it
		try: # attempt to parse the string as a float
			newString = float(string)
		except ValueError:
			return string # if it fails, just return the string
		return newString # if it's successful, return the parsed float

	def get_headers(self): # accessor for list of headers
		return self.headers

	def get_types(self): # accessor for list of types
		return self.types

	def get_num_dimensions(self): # returns number of columns
		return ( self.data.shape[1] )

	def get_num_points(self): # returns number of rows
		return ( self.data.shape[0] )

	def get_row(self, rowIndex): # returns the specified row as a NumPy matrix
		# return ( self.rows[rowIndex] )
		return ( self.data[rowIndex,] )

	def get_value(self, header, rowIndex): # returns the specified value in the given column
		if header in self.header2col: # as long as the header is in the dict
			return ( self.data.item((rowIndex, self.header2col[header])) )
		else: # print alert message
			print("\n\n\tThere is no header by the name of '", header, "'\n", sep='')
			return

	def get_data(self): # returns the numpy matrix of all parsed data.
		return self.data

	def choose_columns(self, columns): # uses list of header names to select columns
		dataSplit = np.hsplit( self.data, self.get_num_dimensions() )
		colTargets = []
		for col in range(len(columns)):
			colTargets.append(dataSplit[self.header2col[columns[col]]])
		return np.hstack(colTargets)

	def add_column(self, column, header = "NewHeader"): # adds the given column to the data matrix
		# if either the height is incorrect or it's wider than one unit
		if (column.shape[0] != self.data.shape[0]) or (column.shape[1] != 1):
			# if they accidentally put in the transpose
			if (column.shape[1] == self.data.shape[0]):
				print("Hey dummy--you put the column in sideways!")
			else:
				# alert the user to their mistake
				print("Whoops! The dimensions of the column you're",
				"trying to add should be", self.data.shape[0], "by 1.")
		else:
			# smash the last column onto the right side of the existing data matrix
			self.data = np.hstack((self.data, column))
			# add a header for it (if one isn't given, uses "NewHeader")
			self.headers.append(header)

	def write(self, filename, headers = None):
		if (headers == None):
			headers = self.get_headers()
		# create a matrix of the data for the chosen columns
		chosen_data = self.choose_columns(headers)
		# assign to the variable file the open file of the given filename
		file = open(filename, 'w')
		# write each column
		for i in range(len(headers)):
			file.write(headers[i])
			# if not the last column
			if (i != (len(headers) - 1)):
				file.write(', ')
		file.write("\n")
		# for the number of rows in the chosen data
		for i in range(chosen_data.shape[0]):
			# for the number of columns in the chosen data
			for j in range(chosen_data.shape[1]):
				# write the piece of data at i, j
				file.write( str(chosen_data[i,j]) )
				# if not the last column
				if j != (chosen_data.shape[1] - 1):
					file.write(', ')
			file.write(', ')
		print("Successfully written to %s.", filename)

def main(argv):
	testee = Data(sys.argv[1])
	print("\n\nData Range:\n", anal.data_range( testee.get_headers(), testee ), "\n\n\n----")
	print("\n\nMean:\n", anal.mean( testee.get_headers(), testee ), "\n\n\n----")
	print("\n\nStDev:\n", anal.stdev( testee.get_headers(), testee ), "\n\n\n----")
	print("\n\nSeparately Normalized Columns:\n", anal.normalize_columns_separately( testee.get_headers(), testee ), "\n\n\n----")
	print("\n\nColumns Normalized Together:\n", anal.normalize_columns_together( testee.get_headers(), testee ), "\n\n\n----")
	print("\n\nHeaders:\n", testee.get_headers(), "\n\n\n----")
	print("\n\nChosen Columns:\n", testee.choose_columns( [ testee.get_headers()[0], testee.get_headers()[0] ] ))

if __name__ == "__main__":
	main(sys.argv)