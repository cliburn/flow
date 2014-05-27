"""Need type, Plot() and ModelUpdate()."""
import wx
#import vtk
import os
import sys
#sys.path.append(".")
from wxPlots import PlotPanel
from numpy import arange

#from vtk.wx.wxVTKRenderWindow import wxVTKRenderWindow

from VizFrame import VizFrame

class SimpleFrame(VizFrame):
    """frame for viewing simple x-y plots"""
    type = 'X-Y plot'

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Simple"):
        VizFrame.__init__(self, parent, id, pos, title)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self, -1)

        self.widget = SimplePanel(self, None)
        self.widget.draw()

        self.MenuBar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.MenuBar.Append(self.FileMenu, "File")
        self.SetMenuBar(self.MenuBar)
        export = self.FileMenu.Append(-1, "Export graphics")
        self.Bind(wx.EVT_MENU, self.OnExport, export)
        
        self.RadioButtons(['none'])
        self.box.Add(self.panel, 0, wx.EXPAND)
        self.box.Add(self.widget, 1, wx.EXPAND)
        self.SetSizer(self.box)
        self.Show()
        
    def OnExport(self, event):
        print "Test export graphics"
        self.widget.export()

    def RadioButtons(self, list):
        try:
            self.radioX.Destroy()
        except AttributeError:
            pass
        self.radioX = wx.RadioBox(self.panel, -1, "Variable", (10,10), wx.DefaultSize, list, 1, wx.RA_SPECIFY_COLS)
        self.radioX.Bind(wx.EVT_RADIOBOX, self.OnControlSwitch)

    def UpdateSimple(self, x):
        self.widget.x = self.model.current_array[:,x]
        self.widget.name = str(x)
        self.widget.draw()
        
    def Plot(self):
        try:
            if self.model.ready:
              self.RadioButtons(map(str,range(1, self.model.current_array.shape[1]+1)))
              self.UpdateSimple(self.radioX.GetSelection())
            else:
              pass
        except AttributeError:
            pass

    def OnControlSwitch(self,event):
        self.UpdateSimple(self.radioX.GetSelection())
    
    def ModelUpdate(self,model):
        self.model = model
        self.Plot()

class SimplePanel(PlotPanel):
    """An example plotting panel. The only method that needs overriding is the draw method"""
    def __init__(self,parent, x, name='', **kwargs):
        self.x = x
        PlotPanel.__init__( self, parent, **kwargs )

    def draw(self):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
        self.subplot.clear()
        if self.x is not None:
            # sample just 1000 points
            if len(self.x) > 999:
                stride = len(self.x)/999
            else:
                stride = 1
            x = self.x[:999*stride:stride]

            self.subplot.plot(stride*arange(len(x)), x, 'b-')
        self.Refresh()

