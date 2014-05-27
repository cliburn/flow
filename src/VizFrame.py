import wx
#import vtk
#from vtk.wx.wxVTKRenderWindow import wxVTKRenderWindow
#import wx.grid

class VizFrame(wx.Frame):
    """default frame class for vizualization"""
    type = "Basic Frame"
    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="No Title Set"):
        """creates default frame"""
        wx.Frame.__init__(self,parent,id,title, pos)
        self.model = None
        
    def AttachModel(self,model):
        self.ModelUpdate(model)

    def ModelUpdate(self,model):
        self.model = model
        
       

