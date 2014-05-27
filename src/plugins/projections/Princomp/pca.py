# This code is copied verbatim from
# http://itb.biologie.hu-berlin.de/~zito/teaching/CNSIV/30.04.2004.html
# and is not meant for production use but simply to illustrate how
# simple it is to write sucn a projection plugin in Python 
#
# PCA code is by Tiziano Zito at the Institute for Theoretical
# Biology, Humboldt University Berlin


#########################################################################
# Hi! If you came here searching for Python PCA in google, note that    #
# this is a script for a lecture. If you are looking for Python code to #
# perform PCA, check out: http://mdp-toolkit.sourceforge.net .          #
#########################################################################

# The following 4 lines are needed to import the modules
# necessary to do scientific calculations and plotting.
# the syntax 
# from module import *
# imports all objects in the module to the local name space 
from scipy import *
from numpy import dot
from numpy.linalg import eig
# from numpy.linalg import symeig
# from gracePlot import gracePlot as figure
# from utils import *

# definition of the function to perform pca or whitening
# white = 0 means that the default value of the parameter
# white will be 0. if you call the function like this:
# matrix=pca(x)
# the function will assume white=0. if this is not what
# you want, then do:
# matrix=pca(x,white=1)
def pca(x, white = 0):
    # the lines between triple quotes: """..."""
    # are documentation lines. they appear when you 
    # do:
    # >>> from pca import pca
    # >>> help(pca)
    """
       function to perform Principal Component Analysis.
    """
    # we are here assuming that x is a multidimensional
    # array (let's say a matrix Nx2) and that different
    # data points are stored on different raws. Basically
    # we assume this structure for x:
    # x = [[ X0, Y0 ],
    #      [ X1, Y1 ],
    #      ..........,
    #      [ XN-1,YN-1 ]]
    # tlen will then be the number of rows.
    # note the use of the attribute x.shape to get the number
    # of rows.
    tlen = x.shape[0]
    avg = mean(x, axis = 0)

    # remove the average!!!
    x = x - avg

    # covariance matrix
    cov_mat = dot(transpose(x),x) / (tlen - 1)

    # get eigenvalues and eigenvectors of the covariance matrix
    # we use the funciton symeig because the matrix is symmetric
    # and definite positive.
    eigval,eigvec = eig(cov_mat)
    # eigval,eigvec = symeig(cov_mat)
    
    # we swap the eigenvalue array and the eigenvector matrix
    # because we want them is descending order (so that the 
    # first eigenvalue is the larger one).
    eigval = eigval[::-1]
    eigvec = fliplr(eigvec)

    if white:
        # whitening
        eigval = eigval**(-0.5)
        eigvec = eigvec*eigval

    # return x in the new coordinate system
    return dot(x,eigvec)
    

# the following lines are executed only if you call this file
# lilke this:
# python pca.py
# if you are already running the interpreter, you could instead
# import the only the function "pca" and apply it on your data.
# in this case you would do:
# >>> from pca import pca
if __name__ == '__main__':
    # create two random series with variance 5 and 1 and 
    # mean 4 and -6
    x1 = randn(1000)*5 + 4
    x2 = randn(1000)*1 - 6
    
    # create the matrix of the data points in the format
    # specified inthe function pca
    mat = transpose(array([x1,x2]))
   
    # rotate the matrix just to have fun
    mat = rotate(mat,45,units='degrees')
   
    # perform pca
    matpca = pca(mat)

    # perform whitening
    matwhite = pca(mat,white = 1)

    # open a figure
    fig = figure()

    # to plot more datasets (whithout overwriting)
    fig.hold(1)

    # plot the data sets without lines and with points as circles
    fig.plot(mat[:,0],mat[:,1],symbols=1,symbolsize=24,line=0)
    fig.plot(matpca[:,0],matpca[:,1],symbols=1,symbolsize=24,line=0)
    fig.plot(matwhite[:,0],matwhite[:,1],symbols=1,symbolsize=24,line=0)

    # rescale the axis
    fig.ylimit(lower=-20,upper=20)
    fig.xlimit(lower=-20,upper=20)
    fig.redraw()

    # end!

