"""Test if ML picks up correct number of components."""

from numpy import *
from numpy.random import multivariate_normal, shuffle
import bayes
import pylab

if __name__ == '__main__':
    
    # a 3 component 3D multivariate mixture
    mu = array([[10.0, 19.0, 25.0], [10.0, 19.0, 25.0], [10.0, 19.0, 25.0]])
    Sigma = zeros((3,3,3));
    for i in range(3):
        Sigma[:,:,i] = 2.5*eye(3) 

    x  = transpose(concatenate(
            (multivariate_normal(mu[:,0], Sigma[:,:,0], (150)),
             multivariate_normal(mu[:,1], Sigma[:,:,1], (100)),
             multivariate_normal(mu[:,2], Sigma[:,:,2], (500)))))

    nit = 0
    nmc = 100
    n = x.shape[1]
    p = x.shape[0]
    record = 0
    
    bics = []

    for k in range(1, 6):

        npars = k + k*p + k*p*(p-1)/2

        b = bayes.Bayes()
        b.init(x, n, p, k)
        b.mcmc(nit, nmc, ".bayes.out", record)

        bics.append(b.get_loglik() - 0.5*log(n)*npars)

    pylab.clf()
    pylab.plot(range(1, 6), bics, '-o')
    ax = pylab.axis()
    pylab.axis([0, 6, ax[2], ax[3]])
    pylab.xlabel('Number of components (k)')
    pylab.ylabel('BIC')
    pylab.show()

