from plugin import Projections
import mdp
from numpy import dot, array
import wx

class PcaPy(Projections):
    name = "PcaPy"
    def Main(self,model):
        # self.model = model
        data = array(model.GetCurrentData()[:])

        k = wx.GetNumberFromUser("PCA Dialog",
                                 "Enter number of principal components",
                                 "k",
                                 1)

        pca_data = mdp.pca(data, output_dim=k)
        # ica_data = r.fastICA(data, k, alg_typ = "deflation", fun = "logcosh", alpha = 1, method = "R", row_norm = 0, maxit = 200, tol = 0.0001, verbose = 1)
        fields = ['Comp%02d' % c for c in range(1, k+1)]
        model.updateHDF('PcaPY', pca_data, fields=fields)
        
