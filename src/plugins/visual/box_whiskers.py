import wx
from wxPlots import PlotPanel

from VizFrame import VizFrame

class BoxWhiskersFrame(VizFrame):
    """Box and whiskers plot"""
    type = "Box and whiskers"

    def __init__(self, parent=None, id=-1, pos=wx.DefaultPosition, title="Box and Whiskers"):
        VizFrame.__init__(self, parent, id, pos, title)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self, -1)

        self.widget = BoxWhiskersPanel(self)
        self.widget.draw()

        self.MenuBar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.MenuBar.Append(self.FileMenu, "File")
        self.SetMenuBar(self.MenuBar)
        export = self.FileMenu.Append(-1, "Export graphics")
        self.Bind(wx.EVT_MENU, self.OnExport, export)

        self.box.Add(self.panel, 0, wx.EXPAND)
        self.box.Add(self.widget, 1, wx.EXPAND)
        self.SetSizer(self.box)
        self.Show()

    def OnExport(self, event):
        self.widget.export()

    def Plot(self):
        try:
            if self.model.ready:
                self.widget.data = self.model.current_array[:]
                if len(self.widget.data.shape) == 2:
                    self.widget.labels = map(str, range(self.widget.data.shape[1]))
                else:
                    self.widget.labels = self.model.GetCurrentData().getAttr('fields')
                    self.widget.data = self.model.GetCurrentData()[:]
                    

                self.widget.draw()
            else:
                pass
        except AttributeError, e:
            print e
            pass

class BoxWhiskersPanel(PlotPanel):
    """Box and whiskers plot."""
    def __init__(self, parent, **kwargs):
        #super(BoxWhiskersPanel, self).__init__(*args)
        self.labels = None
        self.data = None
        PlotPanel.__init__( self, parent, **kwargs )
        
    def draw(self):
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
        self.subplot.clear()
        if self.data is not None:
            self.subplot.boxplot(self.data)
        if self.labels is not None:
            self.subplot.set_xticklabels(self.labels)
        self.Refresh()
