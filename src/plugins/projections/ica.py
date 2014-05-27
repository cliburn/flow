from plugin import Projections
from rpy import r
from numpy import dot, array
import wx

r.library("fastICA")

class Ica(Projections):
    name = "Ica"
    def Main(self,model):
        # self.model = model
        data = array(model.GetCurrentData()[:])

        k = wx.GetNumberFromUser("ICA Dialog",
                                 "Enter number of independent components",
                                 "k",
                                 1)

        ica_data = r.fastICA(data, k, alg_typ = "deflation", fun = "logcosh", alpha = 1, method = "R", row_norm = 0, maxit = 200, tol = 0.0001, verbose = 1)
        fields = ['Comp%02d' % c for c in range(1, k+1)]
        model.updateHDF('ICA', ica_data['S'], fields=fields)
        
