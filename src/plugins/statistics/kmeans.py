"""Calculate K meanss clustering"""
from plugin import Statistics
import wx
from numpy import array
try:
    from Pycluster import kcluster
except ImportError:
    from Bio.Cluster import kcluster

class KMeans(Statistics):
    """plugin for calculating kmeans"""
    name = "Kmeans"
    def Main(self, model):
        """calculate kmeans"""
        self.model = model
        data = self.model.GetCurrentData()[:]
        
        nclusters = wx.GetNumberFromUser("Kmeans Dialog",
                                         "Enter number of clusters",
                                         "Kmeans nclusters",
                                         1)

        z, error, found = kcluster(data, nclusters=nclusters) #IGNORE:W0612
        self.model.NewGroup('Kmeans%02d' % nclusters)
        self.model.hdf5.createArray(self.model.current_group, 'z', array(z))
        self.model.update()
        
        
