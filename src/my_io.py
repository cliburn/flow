"""basic object to handle input and output for the model object"""
from Model import FlowModel
from plugin import addMethod, loadOpen
import wx
import os

class Io(object):
    def __init__(self, model, frame):
        self.model = model
        self.frame = frame
        self.openers = {}
        self.savers = {}
        self.filters = {}
        self.styles = {}
        self.ids = {}
        self.defaultDir=os.path.abspath("../data")
        
    def OnOpen(self, event):
        readType =  self.ids[event.GetId()]
        if self.styles[readType] == 'open':
            style = wx.OPEN
        else:
            style = wx.SAVE
        dlg = wx.FileDialog(self.frame,
                            wildcard=self.filters[readType],
                            defaultDir=self.defaultDir,
                            style=style)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.defaultDir = os.path.split(file)[0]
            self.__getattribute__(readType)(file)
            self.model.savedAs = os.path.splitext(file)[0] + '.h5'
        
        self.model.update()
    
    def OnSave(self,event):
        pass
    
    def LoadPlugins(self):
        desc, methods, filter, style = loadOpen('plugins/io')
        for tag in desc.keys():
            addMethod(self, methods[tag])
            self.openers[tag] = desc[tag]
            self.filters[tag] = filter[tag]
            self.styles[tag] = style[tag]

    def BuildOpenMenu(self, menu=None):
        if menu is None:
            menu = wx.Menu()

        read_methods = [tag for tag in self.openers.keys() if self.styles[tag] == 'open']
        write_methods = [tag for tag in self.openers.keys() if self.styles[tag] == 'save']

        for tag in read_methods: # self.openers.keys():
            item = menu.Append(-1,self.openers[tag])
            self.ids[item.GetId()] = tag
            self.frame.Bind(wx.EVT_MENU, self.OnOpen, item)
        menu.AppendSeparator()
        for tag in write_methods: # self.openers.keys():
            item = menu.Append(-1,self.openers[tag])
            self.ids[item.GetId()] = tag
            self.frame.Bind(wx.EVT_MENU, self.OnOpen, item)
        # return menu
    
    def ModelUpdate(self, model):
        self.model = model
            
if __name__ == '__main__':
    model = FlowModel()
    io = Io(model)
    io.LoadPlugins()
    print io.openers
    io.ReadCSV('../data/3FITC-4PE.004.csv')
    print io.model.data
    
