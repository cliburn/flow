"""Obtain mu, pi and omega from k-means cluster."""

try:
    from Pycluster import kcluster
except ImportError:
    from Bio.Cluster import kcluster
from numpy import *
from numpy.random import multivariate_normal, normal
from numpy.linalg import inv, pinv
from numpy.linalg.linalg import LinAlgError
import sys
sys.path.append('../bindings')
import bayes

def get_mvn_pars(x, nclusters):
#     n, p = x.shape
#     pis = ones(nclusters)/nclusters
#     mus = normal(0, 1, (nclusters, p))
#     omegas = [identity(p) for i in range(nclusters)]

    z, error, found = kcluster(x, nclusters=nclusters)
    z = array(z)
    n = len(z)

    pis = []
    mus = []
    omegas = []

    for i in range(nclusters):
        cluster = x[z==i]
        pi = len(cluster)/float(n)
        mu = mean(cluster, 0)
        sigma = (1.0/len(cluster))*dot(transpose(cluster - mu), (cluster - mu))

        pis.append(pi)
        mus.append(mu)
        try:
            omegas.append(inv(sigma))
        except LinAlgError:
            omegas.append(identity(x.shape[1]))

    return pis, mus, omegas

if __name__ == '__main__':
    # a 3 component 3D multivariate mixture
    mu = array([[10.0, 19.0, 25.0], [10.0, 19.0, 25.0], [10.0, 19.0, 25.0]])
    Sigma = zeros((3,3,3));
    for i in range(3):
        Sigma[:,:,i] = 2.5*eye(3) 

    x  = concatenate(
        (multivariate_normal(mu[:,0], Sigma[:,:,0], (1500)),
         multivariate_normal(mu[:,1], Sigma[:,:,1], (1000)),
         multivariate_normal(mu[:,2], Sigma[:,:,2], (5000))))

    pis, mus, omegas = get_mvn_pars(x, 3)
    for omega in omegas:
        print diag(omega)

    n, p = x.shape
    k = 3
    b = bayes.Bayes()
    b.init(transpose(x), n, p, k)
    b.set_pi(pis)
    b.set_mu(mus)
    b.set_Omega(omegas)
    b.mcmc(0, 200, ".out", False)
    
