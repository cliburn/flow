#! /usr/bin/python
#
# Copyrighted David Cournapeau
# Last Change: Wed Dec 06 09:00 PM 2006 J

# The MIT License

# Copyright (c) <year> <copyright holders>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# New version, with default numpy ordering.

import numpy as N
import numpy.linalg as lin
from numpy.random import randn
from scipy.stats import chi2

# Error classes
class DenError(Exception):
    """Base class for exceptions in this module.
    
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error"""
    def __init__(self, message):
        self.message    = message
    
    def __str__(self):
        return self.message

#============
# Public API
#============
# The following function do all the fancy stuff to check that parameters
# are Ok, and call the right implementation if args are OK.
def gauss_den(x, mu, va, log = False, axis = -1):
    """ Compute multivariate Gaussian density at points x for 
    mean mu and variance va along specified axis:
        
    requirements:
        * mean must be rank 0 (1d) or rank 1 (multi variate gaussian)
        * va must be rank 0 (1d), rank 1(multi variate, diag covariance) or rank 2 
        (multivariate, full covariance).
        * in 1 dimension case, any rank for mean and va is ok, as long as their size
        is 1 (eg they contain only 1 element)
    
    Caution: if x is rank 1, it is assumed you have a 1d problem. You cannot compute
    the gaussian densities of only one sample of dimension d; for this, you have
    to use a rank 2 !

    If log is True, than the log density is returned 
    (useful for underflow ?)"""

    # If data is rank 1, then we have 1 dimension problem.
    if x.ndim == 1:
        d   = 1
        n   = x.size
        if not N.size(mu) == 1:
            raise DenError("for 1 dimension problem, mean must have only one element")
            
        if not N.size(va) == 1:
            raise DenError("for 1 dimension problem, mean must have only one element")
        
        return _scalar_gauss_den(x, mu, va, log)
    # If data is rank 2, then we may have 1 dimension or multi-variate problem
    elif x.ndim == 2:
        oaxis   = (axis + 1) % 2
        n       = x.shape[axis]
        d       = x.shape[oaxis]

        # Get away with 1d case now
        if d == 1:
            return _scalar_gauss_den(x, mu, va, log)

        # Now, d > 1 (numpy attributes should be valid on mean and va now)
        if not N.size(mu) == d or not mu.ndim == 1:
            raise DenError("data is %d dimension, but mean's shape is %s" \
                    % (d, N.shape(mu)) + " (should be (%d,))" % d)
            
        isfull  = (va.ndim == 2)
        if not (N.size(va) == d or (isfull and va.shape[0] == va.shape[1] == d)):
            raise DenError("va has an invalid shape or number of elements")

        if isfull:
            # Compute along rows
            if oaxis == 0:
                return  _full_gauss_den(x, mu[:, N.newaxis], va, log, axis)
            else:
                return  _full_gauss_den(x, mu, va, log, axis)
        else:
            return _diag_gauss_den(x, mu, va, log, axis)
    else:
        raise RuntimeError("Sorry, only rank up to 2 supported")
        
# To plot a confidence ellipse from multi-variate gaussian pdf
def gauss_ell(mu, va, dim = [0, 1], npoints = 100, level = 0.39):
    """ Given a mean and covariance for multi-variate
    gaussian, returns npoints points for the ellipse
    of confidence given by level (all points will be inside
    the ellipsoides with a probability equal to level)
    
    Returns the coordinate x and y of the ellipse"""
    
    c       = N.array(dim)

    if mu.size < 2:
        raise RuntimeError("this function only make sense for dimension 2 and more")

    if mu.size == va.size:
        mode    = 'diag'
    else:
        if va.ndim == 2:
            if va.shape[0] == va.shape[1]:
                mode    = 'full'
            else:
                raise DenError("variance not square")
        else:
            raise DenError("mean and variance are not dim conformant")

    # If X ~ N(mu, va), then [X` * va^(-1/2) * X] ~ Chi2
    chi22d  = chi2(2)
    mahal   = N.sqrt(chi22d.ppf(level))
    
    # Generates a circle of npoints
    theta   = N.linspace(0, 2 * N.pi, npoints)
    circle  = mahal * N.array([N.cos(theta), N.sin(theta)])

    # Get the dimension which we are interested in:
    mu  = mu[dim]
    if mode == 'diag':
        va      = va[dim]
        elps    = N.outer(mu, N.ones(npoints))
        elps    += N.dot(N.diag(N.sqrt(va)), circle)
    elif mode == 'full':
        va  = va[c,:][:,c]
        # Method: compute the cholesky decomp of each cov matrix, that is
        # compute cova such as va = cova * cova' 
        # WARN: scipy is different than matlab here, as scipy computes a lower
        # triangular cholesky decomp: 
        #   - va = cova * cova' (scipy)
        #   - va = cova' * cova (matlab)
        # So take care when comparing results with matlab !
        cova    = lin.cholesky(va)
        elps    = N.outer(mu, N.ones(npoints))
        elps    += N.dot(cova, circle)
    else:
        raise DenParam("var mode not recognized")

    return elps[0, :], elps[1, :]

#=============
# Private Api
#=============
# Those 3 functions do almost all the actual computation
def _scalar_gauss_den(x, mu, va, log):
    """ This function is the actual implementation
    of gaussian pdf in scalar case. It assumes all args
    are conformant, so it should not be used directly
    
    Call gauss_den instead"""
    inva    = 1/va
    fac     = (2*N.pi) ** (-1/2.0) * N.sqrt(inva)
    y       = ((x-mu) ** 2) * -0.5 * inva
    if not log:
        y   = fac * N.exp(y.ravel())
    else:
        y   = y + log(fac)

    return y
    
def _diag_gauss_den(x, mu, va, log, axis):
    """ This function is the actual implementation
    of gaussian pdf in scalar case. It assumes all args
    are conformant, so it should not be used directly
    
    Call gauss_den instead"""
    # Diagonal matrix case
    d   = mu.size
    if axis % 2 == 0:
        x  = N.swapaxes(x, 0, 1)

    if not log:
        inva    = 1/va[0]
        fac     = (2*N.pi) ** (-d/2.0) * N.sqrt(inva)
        y       =  (x[0] - mu[0]) ** 2 * inva * -0.5
        for i in range(1, d):
            inva    = 1/va[i]
            fac     *= N.sqrt(inva)
            y       += (x[i] - mu[i]) ** 2 * inva * -0.5
        y   = fac * N.exp(y)
    else:
        y   = _scalar_gauss_den(x[0], mu[0], va[0], log)
        for i in range(1, d):
            y    +=  _scalar_gauss_den(x[i], mu[i], va[i], log)

    return y

def _full_gauss_den(x, mu, va, log, axis):
    """ This function is the actual implementation
    of gaussian pdf in full matrix case. 
    
    It assumes all args are conformant, so it should 
    not be used directly Call gauss_den instead
    
    Does not check if va is definite positive (on inversible 
    for that matter), so the inverse computation and/or determinant
    would throw an exception."""
    d       = mu.size
    inva    = lin.inv(va)
    fac     = 1 / N.sqrt( (2*N.pi) ** d * N.fabs(lin.det(va)))

    # # Slow version (does not work since version 0.6)
    # n       = N.size(x, 0)
    # y       = N.zeros(n)
    # for i in range(n):
    #     y[i] = N.dot(x[i,:],
    #              N.dot(inva, N.transpose(x[i,:])))
    # y *= -0.5

    # we are using a trick with sum to "emulate" 
    # the matrix multiplication inva * x without any explicit loop
    if axis % 2 == 1:
        y   = N.dot(inva, (x-mu))
        y   = -0.5 * N.sum(y * (x-mu), 0)
    else:
        y   = N.dot((x-mu), inva)
        y   = -0.5 * N.sum(y * (x-mu), 1)

    if not log:
        y   = fac * N.exp(y)
    else:
        y   = y + N.log(fac)
 
    return y

if __name__ == "__main__":
    import pylab

    #=========================================
    # Test plotting a simple diag 2d variance:
    #=========================================
    va  = N.array([5, 3])
    mu  = N.array([2, 3])

    # Generate a multivariate gaussian of mean mu and covariance va
    X       = randn(2, 1e3)
    Yc      = N.dot(N.diag(N.sqrt(va)), X)
    Yc      = Yc.transpose() + mu

    # Plotting
    Xe, Ye  = gauss_ell(mu, va, npoints = 100)
    pylab.figure()
    pylab.plot(Yc[:, 0], Yc[:, 1], '.')
    pylab.plot(Xe, Ye, 'r')

    #=========================================
    # Test plotting a simple full 2d variance:
    #=========================================
    va  = N.array([[0.2, 0.1],[0.1, 0.5]])
    mu  = N.array([0, 3])

    # Generate a multivariate gaussian of mean mu and covariance va
    X       = randn(1e3, 2)
    Yc      = N.dot(lin.cholesky(va), X.transpose())
    Yc      = Yc.transpose() + mu

    # Plotting
    Xe, Ye  = gauss_ell(mu, va, npoints = 100, level=0.95)
    pylab.figure()
    pylab.plot(Yc[:, 0], Yc[:, 1], '.')
    pylab.plot(Xe, Ye, 'r')
    pylab.show()
