# Ben Capodanno; Template by Bruce Maxwell
# CS 251 Project 8
# classifiers.py
# This file contains classifier classes for classifying data
# Original: pring 2015. Updated: April 21, 2019

import sys
import data
import math
import string
import analysis as an
import numpy as np

class Classifier:

    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        self._type = type

    def type(self, newtype = None):
        '''Set or get the type with this function'''
        if newtype != None:
            self._type = newtype
        return self._type

    def confusion_matrix( self, truecats, classcats ):
        '''Takes in a Nx1 true cat matrix and a 1xN predicted cat matrix of
        i-index numeric categories and computes the confusion matrix.
        The rows represent true categories, and the columns represent the
        classifier output. To get the number of classes, you can use the
        np.unique function to identify the number of unique categories in the
        truecats matrix.

        '''
        truecats = truecats.flatten()
        # figure out how many categories there are and get the mapping (np.unique)
        num_cat, labels = np.unique( np.array( truecats.T ), return_inverse = True )
        confmtx = np.zeros( ( np.size( num_cat ), np.size( num_cat ) ) )
        for i in range( np.size( truecats ) ):
            confmtx[ truecats[0,i], classcats[i] ] += 1

        return confmtx

    def confusion_matrix_str( self, cmtx ):
        '''Takes in a confusion matrix and returns a string suitable for printing.'''
        s = "\nConfusion Matrix\n               Classified As\nTruth\n      "

        for i in range( np.size( cmtx, 1 ) ):
            s += '{0:>6}'.format( str(i) )

        s += "\n"
        for i in range( np.size( cmtx, 0 ) ):
            s += '{0:>6}'.format( str(i) )

            for j in range( np.size( cmtx, 1 ) ):
                s += '{0:>6}'.format( int( cmtx[i,j] ) )
            s += "\n"

        return s

    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self._type)


class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.

    '''

    def __init__(self, data=None, headers=[], categories=None):
        '''Takes in a Matrix of data with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')

        # create default class variables
        self.data = data
        self.headers = headers
        self.categories = categories
        self.classes = categories
        self.num_classes = 0
        self.num_features = 0
        self.data_labels = None

        # naive bayes unique variables
        self.class_means = None
        self.class_variances = None
        self.class_scales = None
        self.class_priors = None

        # if given data,
        if self.data != None:
            self.build( self.data.subset( self.headers ), self.categories )

    def build( self, A, categories ):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        self.classes, self.data_labels = np.unique( np.array( categories.T ), return_inverse = True )

        # set up qol variables
        self.data = A
        self.categories = categories
        self.num_features = np.size( A, 1 )
        self.num_classes = np.size( self.classes )

        # create the matrices for the means, vars, scales, and priors
        self.class_means = np.empty( ( self.num_classes, self.num_features ) )
        self.class_variances = np.empty( ( self.num_classes, self.num_features ) )
        self.class_scales = np.empty( ( self.num_classes, self.num_features ) )
        self.class_priors = np.empty( ( self.num_classes, 1 ) )

        # compute the means/vars/scales/priors for each class
        for i in range( self.num_classes ):
            curr_class = A[( self.data_labels == i ), :]
            self.class_means[i] = np.mean( curr_class, 0 )
            self.class_variances[i] = np.var( curr_class, 0 )
            self.class_scales[i,] = ( 1 / np.sqrt( ( 2 * math.pi * np.square( np.std( curr_class, 0, ddof = 1 ) ) ) ) )
            self.class_priors[i] = np.size( curr_class, 0 ) / np.size( A, 0 )

        return

    def classify( self, A, return_likelihoods=False ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the probability value for each class, which
        is product of the probability of the data given the class P(Data | Class)
        and the prior P(Class).

        '''

        # error check to see if A has the same number of columns as the class means
        if np.size( A, 1 ) != self.num_features:
            raise ValueError( 'Unmatched Shape. Feature size = ', np.size( A, 1 ),
                              ' does not match classifier current size = ', num_features )
            exit()

        # make a matrix that is N x C to store the probability of each class for each data point
        P = np.empty( ( self.num_classes, np.size( A, 0 ) ) )

        # Calcuate P(D | C) by looping over the classes
        #
        #  To compute the likelihood, use the formula for the Gaussian
        #  pdf for each feature, then multiply the likelihood for all
        #  the features together The result should be an N x 1 column
        #  matrix that gets assigned to a column of P
        for i in range( self.num_classes ):
            P[i] =  np.multiply( self.class_priors[i], np.prod( np.multiply( self.class_scales[i,:],
                    np.exp( np.multiply( -1,
                    np.square( ( A - self.class_means[i,:] ) ) / np.multiply( 2, self.class_variances[i,:] ) ) ) ), 1 ) ).T

        P = P.T

        # calculate the most likely class for each data point
        cats = np.argmax( P, 1 ) # take the argmax of P along axis 1

        # use the class ID as a lookup to generate the original labels
        labels = self.classes[cats]

        if return_likelihoods:
            return cats, labels, P

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.class_means[i,:]) + "\n"
            s += 'Var   : ' + str(self.class_variances[i,:]) + "\n"
            s += 'Scales: ' + str(self.class_scales[i,:]) + "\n"
            s += 'Priors: ' + str(self.class_priors[i,0]) + "\n"

        s += "\n"
        return s

    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return


class KNN(Classifier):

    def __init__(self, data=None, headers=[], categories=None, K=None):
        '''Take in a Matrix of data with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')

        # create default class variables
        self.data = data
        self.headers = headers
        self.categories = categories
        self.classes = categories

        # original class labels
        self.data_labels = None
        self.num_classes = 0
        self.num_features = 0

        # unique data for the KNN classifier: list of exemplars (matrices)
        self.K = K
        self.exemplars = []

        # if given data,
        if data != None:
            self.build( self.data.subset( self.headers ), self.categories, self.K )

    def build( self, A, categories, K = None ):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        self.classes, self.data_labels = np.unique( np.array( categories.T ), return_inverse = True )

        # set up qol variables
        self.categories = categories
        self.num_features = np.size( A, 1 )
        self.num_classes = np.size( self.classes )

        # for each category i, build the set of exemplars
        for i in range( len( self.classes ) ):
            if K is None:
                # append to exemplars a matrix with all of the rows of A where the category/mapping is i
                self.exemplars.append( A[( self.data_labels == i ), :] )
            else:
                # run K-means on the rows of A where the category/mapping is i
                codebook, codes, errors, quality = an.kmeans( A[( self.data_labels == i ), :], [], K, False )
                self.exemplars.append( codebook )

        return

    def classify( self, A, return_distances = False, K = 3 ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_distances is
        True, it also returns the NxC distance matrix. The distance is
        calculated using the nearest K neighbors.'''

        # error check to see if A has the same number of columns as the class means
        if np.size( A, 1 ) != self.num_features:
            raise ValueError( 'Unmatched Shape. Feature size = ', np.size( A, 1 ),
                              ' does not match classifier current size = ', num_features )
            exit()

        # make a matrix that is N x C to store the distance to each class for each data point
        D = np.zeros( ( self.num_classes, np.size( A, 0 ) ) ) # a matrix of zeros that is N (rows of A) x C (number of classes)

        for i in range( self.num_classes ):
            # make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
            tmp = np.zeros( ( np.size( A, 0 ), np.size( self.exemplars[i], 0 ) ) )

            # calculate the distance from each point in A to each point in exemplar matrix i (for loop)
            for j in range( np.size( A, 0 ) ):
                # *** how to do in one line with indexing???
                for k in range( np.size( self.exemplars[i], 0 ) ):
                    tmp[j,k] = np.sum( np.square( A[j] - self.exemplars[i][k] ) )

            # sort the distances by row and sum the first K columns
            tmp = np.sort( tmp, 1 )
            dist = np.sum( tmp[:,0:K], axis = 1 )

            # this is the distance to the first class
            D[i] = dist


        D = D.T

        # calculate the most likely class for each data point
        cats = np.argmin( D, 1 )

        # use the class ID as a lookup to generate the original labels
        labels = self.classes[cats]

        if return_distances:
            return cats, labels, D

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):
        '''Writes the KNN classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the KNN classifier from the file'''
        # extension
        return


# test function
def main(argv):
    # test function here
    if len(argv) < 3:
        print( 'Usage: python %s <training data file> <test data file> <optional training categories file> <optional test categories file>' % (argv[0]) )
        print( '    If categories are not provided as separate files, then the last column is assumed to be the category.')
        exit(-1)

    train_file = argv[1]
    test_file = argv[2]
    dtrain = data.Data(train_file)
    dtest = data.Data(test_file)


    if len(argv) >= 5:
        train_headers = dtrain.get_headers()
        test_headers = dtrain.get_headers()

        traincat_file = argv[3]
        testcat_file = argv[4]

        traincats = data.Data(traincat_file)
        traincatdata = traincats.subset(traincats.get_headers())

        testcats = data.Data(testcat_file)
        testcatdata = testcats.subset(testcats.get_headers())

    else:
        train_headers = dtrain.get_headers()[:-1]
        test_headers = dtrain.get_headers()[:-1]

        traincatdata = dtrain.subset([dtrain.get_headers()[-1]])
        testcatdata = dtest.subset([dtest.get_headers()[-1]])


    nbc = NaiveBayes(dtrain, train_headers, traincatdata )

    print( 'Naive Bayes Training Set Results' )
    A = dtrain.subset(train_headers)

    newcats, newlabels = nbc.classify( A )

    uniquelabels, correctedtraincats = np.unique( traincatdata.T.tolist()[0], return_inverse = True)
    correctedtraincats = np.matrix([correctedtraincats]).T

    confmtx = nbc.confusion_matrix( correctedtraincats, newcats )
    print( nbc.confusion_matrix_str( confmtx ) )

    print( 'Naive Bayes Test Set Results' )
    A = dtest.subset(test_headers)

    newcats, newlabels = nbc.classify( A )

    uniquelabels, correctedtestcats = np.unique( testcatdata.T.tolist()[0], return_inverse = True)
    correctedtestcats = np.matrix([correctedtestcats]).T

    confmtx = nbc.confusion_matrix( correctedtestcats, newcats )
    print( nbc.confusion_matrix_str( confmtx ) )

    print( '-----------------' )
    print( 'Building KNN Classifier' )
    knnc = KNN( dtrain, train_headers, traincatdata, 10 )

    print( 'KNN Training Set Results' )
    A = dtrain.subset(train_headers)

    newcats, newlabels = knnc.classify( A )

    confmtx = knnc.confusion_matrix( correctedtraincats, newcats )
    print( knnc.confusion_matrix_str(confmtx) )

    print( 'KNN Test Set Results' )
    A = dtest.subset(test_headers)

    newcats, newlabels = knnc.classify(A)

    # print the confusion matrix
    confmtx = knnc.confusion_matrix( correctedtestcats, newcats )
    print( knnc.confusion_matrix_str(confmtx) )

    return

if __name__ == "__main__":
    main(sys.argv)
