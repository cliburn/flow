from plugin import Projections
import mdp
from numpy import dot, array
import wx

class IcaPy(Projections):
    name = "IcaPy"
    def Main(self,model):
        # self.model = model
        data = array(model.GetCurrentData()[:])

        k = wx.GetNumberFromUser("ICA Dialog",
                                 "Enter number of independent components",
                                 "k",
                                 1)

        ica_node = mdp.nodes.FastICANode()
        ica_node.set_output_dim(k)
        ica_data = mdp.fastica(data)

        # ica_data = r.fastICA(data, k, alg_typ = "deflation", fun = "logcosh", alpha = 1, method = "R", row_norm = 0, maxit = 200, tol = 0.0001, verbose = 1)
        fields = ['Comp%02d' % c for c in range(1, k+1)]
        model.updateHDF('IcaPY', ica_data, fields=fields)
        
