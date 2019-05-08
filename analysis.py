# CS251 - Project 2 - analysis.py - Max Perrello - 3/8/19
import numpy as np
import sys
import PCAData
import ClusterData
import scipy.stats as spt
import scipy
import scipy.cluster.vq as vq
import random

def data_range(headers, data): # takes list of headers and data obj,
	# returns list of min/maxs by col
	data = data.choose_columns(headers)
	dataCols = np.hsplit(data, len(headers))
	results = []
	for i in range(len(dataCols)):
		subResults = []
		subResults.append( dataCols[i].min() )
		subResults.append( dataCols[i].max() )
		results.append(subResults)
	return results

def mean(headers, data): # takes list of headers and data obj,
	# returns list of means by col
	data = data.choose_columns(headers)
	dataCols = np.hsplit(data, len(headers))
	results = []
	for i in range(len(dataCols)):
		results.append( dataCols[i].mean() )
	return results

def stdev(headers, data): # takes list of headers and data obj,
	# returns list of stdev by col
	data = data.choose_columns(headers)
	dataCols = np.hsplit(data, len(headers))
	results = []
	for i in range(len(dataCols)):
		results.append( dataCols[i].std() )
	return results

def normalize_columns_separately(headers, data): # takes list of headers and data obj,
	# returns data with independently normalized columns
	dataCols = np.hsplit(data.choose_columns(headers), len(headers))
	results = []
	for i in range(len(dataCols)):
		results.append( (dataCols[i] - dataCols[i].min(0)) / dataCols[i].ptp(0) )
		# ptp() instead of max() \/
		# stackoverflow.com/questions/29661574/normalize-numpy-array-columns-in-python
	return np.matrix(np.hstack(results))

def normalize_columns_together(headers, data): # takes list of headers and data obj,
	# returns data normalized together
	data = data.choose_columns(headers)
	mini = data[data != 0].min()
	maxi = data[data != 0].ptp()
	newData = np.copy(data)
	for (i,j), value in np.ndenumerate(data):
		newData[i,j] = ( (value - mini) / maxi )
	return newData

def single_linear_regression(data_obj, ind_var, dep_var):
	targets = [ind_var, dep_var]
	dataMatrix = data_obj.choose_columns(targets)
	slope, intercept, r_value, p_value, std_err = spt.linregress(dataMatrix)
	return (slope, intercept, r_value, p_value, std_err, np.min(dataMatrix[:,0]),
		np.max(dataMatrix[:,0]), np.min(dataMatrix[:,1]), np.max(dataMatrix[:,1]))

def linear_regression(dataO, indVars, depVar):
	# column of data for the dependent variable
	y = dataO.choose_columns([depVar])
	# columns of data for the independent variables
	A = dataO.choose_columns(indVars)
	# add a column of 1's to A to represent the constant term in the 
	#    regression equation.  Remember, this is just y = mx + b (even 
	#    if m and x are vectors).
	A = np.concatenate( ( A, (np.matrix(np.ones(
		A.shape[0] )).T) ), axis=1)
	AAinv = np.linalg.inv( np.dot(A.T, A))
	#    The matrix A.T * A is the covariance matrix of the independent
	#    data, and we will use it for computing the standard error of the 
	#    linear regression fit below.
	# solves the equation y = Ab
	x = np.linalg.lstsq( A, y )
	# Where A is a matrix of the 
	# independent data, b is the set of unknowns as a column vector, 
	# and y is the dependent column of data.  The return value x 
	# contains the solution for b.
	b = x[0] # solution that provides the best fit regression
	# number of data points (rows in y)
	N = y.shape[0]
	# number of coefficients (rows in b)
	C = b.shape[0]
	# degrees of freedom of the error
	df_e = N - C
	# degrees of freedom of the model fit
	df_r = C - 1
	# error of the model prediction
	error = y - np.dot(A, b)
	# sum squared error
	sse = np.dot(error.T, error) / df_e
	# standard error
	stderr = np.sqrt( np.diagonal( sse[0, 0] * AAinv ) )
	# t-statistic for each independent variable
	t = b.T / stderr
	#    probability of the coefficient indicating a random relationship (slope = 0)
	p = 2*(1 - scipy.stats.t.cdf(abs(t), df_e))
	# r^2 coefficient indicating the quality of the fit.
	r2 = 1 - error.var() / y.var()
	# values of the fit (b), the sum-squared error, the R^2 fit quality,
	# the t-statistic, and the probability of a
	return (b, sse, r2, t, p)

# pca() - takes in list of column headers and returns PCAData object with projected 
# data, eigenvectors, eigenvalues, source data means, and source column headers
def pca(dataO, headers, normalize = True):
	# assign to A the desired data. Use either normalize_columns_separately 
	# or get_data, depending on the value of the normalize argument.
	if normalize == True:
		A = normalize_columns_separately(headers, dataO)
	else:
		A = dataO.choose_columns(headers)
	# assign to m the mean values of the columns of A
	m = np.mean(A, axis=0)
	# assign to D the difference matrix A - m
	D = (A - m)
	# assign to U, S, V the result of running np.svd on D, with full_matrices=False
	U, S, V = np.linalg.svd(D, full_matrices=False)
	# the eigenvalues of cov(A) are the squares of the singular values (S matrix)
	#   divided by the degrees of freedom (N-1). The values are sorted.
	eigenvalues = ( np.square(S) / (len(A) - 1) )
	# project the data onto the eigenvectors. Treat V as a transformation 
	#   matrix and right-multiply it by D transpose. The eigenvectors of A 
	#   are the rows of V. The eigenvectors match the order of the eigenvalues.
	eigenvectors = np.squeeze( np.vsplit( V, V.shape[0] ) )
	projected_data = (V * D.T).T
	# create and return a PCA data object with the headers, projected data, 
	return PCAData.PCAData(projected_data, eigenvectors, eigenvalues, original_means = m, original_headers = headers)
	# eigenvectors, eigenvalues, and mean vector.

# kmeans_numpy - Takes in a Data object, a set of headers, and the number of clusters to create
# Computes and returns the codebook, codes, and representation error.
def kmeans_numpy( d, headers, K, whiten = True):	
	# assign to A the result of getting the data from your Data object
	A = d.choose_columns(headers)
	# assign to W the result of calling vq.whiten on A
	W = vq.whiten(A)
	# assign to codebook, bookerror the result of calling vq.kmeans with W and K
	codebook, bookerror = vq.kmeans(W, K)
	# assign to codes, error the result of calling vq.vq with W and the codebook
	codes, error = vq.vq(W, codebook)
	# return codebook, codes, and error
	return [codebook, codes, error]

# Selects K random rows from the data matrix A and returns them as a matrix
def kmeans_init(A, K):
	# Hint: Probably want to check for error cases (e.g. # data points < K)
	num_rows = A.shape[0]
	if (K > num_rows):
		print("ERROR - K is greater than the number of rows.")
		return
	else:
		# Hint: generate a list of indices then shuffle it and pick K
		# selected_row_indices = (random.shuffle(random.randint(0,num_rows)))[:K]
		# print("K: ", K)
		# print("num_rows: ", num_rows)
		selected_row_indices = random.sample(range(0, (num_rows)), K) # maybe add 1
		# print("selected_row_indices: ", selected_row_indices)
		selected_rows = []
		for i in range(len(selected_row_indices)):
			selected_rows.append( A[selected_row_indices[i],:] )
			# print("Row being grabbed: ", A[selected_row_indices[i],:])
		# print("Finished Matrix: ", np.matrix(selected_rows))
		return np.matrix(selected_rows)

# Given a data matrix A and a set of means in the codebook
# Returns a matrix of the id of the closest mean to each point
# Returns a matrix of the sum-squared distance between the closest mean and each point
def kmeans_classify(A, codebook):
	# Create list to hold indices of closest clusters
	closest_indices = []
	# Create list to hold distance between closest cluster and given points
	closest_distances = []
	# Loop through list of points held in A (each sublist is a point with axis values)
	for i in range(len(A)):
		# Calculate differences between each axis of point and means held in codebook
		mean_diffs = codebook - A[i,:]
		# Create temporary list for holding distance
		temp_dist = []
		# Loop through list of distances between each axis
		for u in range(len(mean_diffs)):
			# Calculate sum squared distance for each cluster mean
			temp_dist.append(np.sqrt(np.sum(np.square(mean_diffs[u]))))
		# Append the smallest distance to closest_distances
		closest_distances.append(np.min(temp_dist))
		# Append the index of the smallest distance to closest_indices
		closest_indices.append(np.argmin(temp_dist))
	# Return each list as a matrix
	return [np.matrix(closest_indices).T, np.matrix(closest_distances).T]

# Given a data matrix A and a set of K initial means, compute the optimal
# cluster means for the data and an ID and an error for each data point
def kmeans_algorithm(A, means, MIN_CHANGE = 1e-7, MAX_ITERATIONS = 100):
	# set up some useful constants
	D = means.shape[1]    # number of dimensions
	K = means.shape[0]    # number of clusters
	N = A.shape[0]        # number of data points
	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS):
		# calculate the codes by calling kemans_classify
		codes, dist = kmeans_classify(A, means)
		# codes[j,0] is the id of the closest mean to point j
		# initialize newmeans to a zero matrix identical in size to means
		newmeans = np.zeros_like(means)
		# Meaning: the new means given the cluster ids for each point
		# initialize a K x 1 matrix counts to zeros
		counts = np.zeros( (K, 1) )
		# Meaning: counts will store how many points get assigned to each mean
		# for the number of data points
		for j in range(N):
			# add to the closest mean (row codes[j,0] of newmeans) the jth row of A
			newmeans[codes[j,0],:] += A[j,:]
			# add one to the corresponding count for the closest mean
			counts[codes[j,0],0] += 1.0
		# finish calculating the means, taking into account possible zero counts
		#for the number of clusters K
		for j in range(K):
			# if counts is not zero, divide the mean by its count
			if (counts[j,0] != 0):
				newmeans[j,:] /= counts[j,0]
			# else pick a random data point to be the new cluster mean
			else:
				newmeans[j,:] = A[random.randint(0,N),:]
		# test if the change is small enough and exit if it is
		diff = np.sum(np.square(means - newmeans))
		means = newmeans
		if diff < MIN_CHANGE:
			break
	# call kmeans_classify one more time with the final means
	codes, errors = kmeans_classify( A, means )
	# return the means, codes, and errors
	return [means, codes, errors, K]

# Takes in a Data object, a set of headers, and the number of clusters to create
# Computes and returns the codebook, codes and representation errors.
def kmeans(d, headers, K, whiten=True ):    
	# assign to A the result getting the data given the headers
	A = d.choose_columns(headers)
	# if whiten is True
	if (whiten == True):
		# assign to W the result of calling vq.whiten on the data
		W = vq.whiten(A)
	# else
	else:
		# assign to W the matrix A
		W = A
	# assign to codebook the result of calling kmeans_init with W and K
	codebook = kmeans_init(W, K)
	# assign to codebook, codes, errors, the result of calling kmeans_algorithm with W and codebook        
	codebook, codes, errors, K = kmeans_algorithm(W, codebook)
	# return the codebook, codes, and representation error
	# return codebook, codes, errors, K
	return ClusterData.ClusterData(codebook, codes, errors, K, d, headers)

def main(argv):
	testMatrix = np.matrix([[1.0,7.0,3.0],[8.0,17.0,11.0],[90.0,24.0,2.0]])
	testHeaders = ["one", "two", "three"]
	data_range(testHeaders, testMatrix)
	print("\n\nSeparately Normalized Columns:\n", normalize_columns_separately(testHeaders, testMatrix), "\n\n----\n\n")
	print("\n\nColumns Normalized Together:\n", normalize_columns_together(testHeaders, testMatrix))

if __name__ == "__main__":
	main(sys.argv)