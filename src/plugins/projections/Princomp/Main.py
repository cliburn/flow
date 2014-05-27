from plugin import Projections
import pca

class Pca(Projections):
    name = "Pca"
    def Main(self,model):
        self.model = model
        pca_data = pca.pca(self.model.GetCurrentData()[:])
        fields = ['Comp%02d' % c for c in range(1, pca_data.shape[1]+1)]
        self.model.updateHDF('PCA', pca_data, fields=fields)

#         self.model.NewGroup('PCA')
#         data = self.model.hdf5.createArray(self.model.current_group, 'data', pca_data)
#         data.setAttr('fields', ['PC%d' % (i+1) for i in range(len(pca_data[0]))])
#         self.model.current_array = data
        
#         self.model.update()
        
