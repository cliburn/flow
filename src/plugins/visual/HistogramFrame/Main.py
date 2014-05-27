"""Need type, Plot() and ModelUpdate()."""
import wx
import sys
import os
from wxPlots import PlotPanel
from numpy import cumsum, linspace, zeros
from VizFrame import VizFrame
from scipy.stats import norm


class HistogramFrame(VizFrame):
    """frame for viewing histograms"""
    type = 'Histogram'

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Histogram"):
        VizFrame.__init__(self, parent, id, pos, title)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self,-1)

        self.widget = HistogramPanel(self, None)
        self.widget.draw()
        
        self.MenuBar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.MenuBar.Append(self.FileMenu, "File")
        self.SetMenuBar(self.MenuBar)
        export = self.FileMenu.Append(-1, "Export graphics")
        self.Bind(wx.EVT_MENU, self.OnExport, export)
        self.AddMenu = wx.Menu()
        self.MenuBar.Append(self.AddMenu, "Add histograms")
        self.AddHist = self.AddMenu.Append(-1, "Add New Histogram")
        self.Bind(wx.EVT_MENU, self.OnAddHist, self.AddHist)
        self.AddMenu.AppendSeparator()
        self.ExtraHists = []

        self.RadioButtons(['none'])
        self.box.Add(self.panel,0,wx.EXPAND)
        self.box.Add(self.widget,1,wx.EXPAND)
        self.SetSizer(self.box)
        self.Show()
    
    def OnAddHist(self, event):
        if not hasattr(self.widget, 'hists'):
            self.widget.hists = {}
        choices = self.model.GetDataGroups()
        dialog = wx.MultiChoiceDialog(None, "Chose data to add to histogram", 'choices', choices)
        if dialog.ShowModal() == wx.ID_OK:
            #print [choices[i] for i in dialog.GetSelections()]
            for groupName in [choices[i]  for i in dialog.GetSelections()]:
                #print groupName
                self.model.SelectGroupByPath(groupName)
                data = self.model.GetCurrentData()
                print data
                if hasattr(data.attrs, 'fields'):
                    newhist = data[:,data.getAttr('fields').index(self.radioX.GetStringSelection())]
                    #self.hists[group] = newhist
                    if groupName not in self.widget.hists.keys():
                        newmenu = self.AddMenu.AppendCheckItem(-1, groupName)
                        newmenu.Check(True)
                        self.Bind(wx.EVT_MENU, self.OnHistSelect, newmenu)
                        self.widget.hists[groupName]= [newhist,True]
                    self.widget.draw()
    
    def OnHistSelect(self, event):
        menuItem = self.AddMenu.FindItemById(event.GetId())
        if menuItem.IsChecked():
            self.widget.hists[menuItem.GetLabel()][1] = True
            #pass
        else:
            self.widget.hists[menuItem.GetLabel()][1] = False
            #pass
        #print menuItem.GetLabel()
        self.widget.draw()
    
    def OnExport(self, event):
        print "Test export graphics"
        self.widget.export()

    def RadioButtons(self,list):
        try:
            self.radioX.Destroy()
        except AttributeError:
            pass
        self.radioX = wx.RadioBox(self.panel,-1,"Marker to plot",(10,10), wx.DefaultSize, list,1,wx.RA_SPECIFY_COLS)
        self.radioX.Bind(wx.EVT_RADIOBOX, self.OnControlSwitch)

    def UpdateHistogram(self, x):
        if len(self.data.shape)== 1:
            self.widget.x = self.data[:]
        else:
            self.widget.x = self.data[:,x]
        fields = self.GetFields()
        self.widget.name = fields[x]
        self.widget.draw()
    
    def GetFields(self):
       try:
            fields = self.data.getAttr('fields')
       except AttributeError:
            fields = []
            if len(self.data.shape)==1:
                fields.append('column')
            else:
                for i in range(len(self.data[1,:])):
                    fields.append('column %d' % i)
       return fields
    def Plot(self):
        try:
            if self.model.ready:
                fields = self.GetFields()
                self.RadioButtons(fields)
                self.UpdateHistogram(self.radioX.GetSelection())
            else:
                pass
        except AttributeError:
            pass

    def OnControlSwitch(self,event):
        self.UpdateHistogram(self.radioX.GetSelection())
    
    def ModelUpdate(self,model):
        self.model = model
        self.data = self.model.GetCurrentData()
        self.Plot()

class HistogramPanel(PlotPanel):
    """An example plotting panel. The only method that needs 
    overriding is the draw method"""
    def __init__(self, parent, x=None, name='', **kwargs):
        self.parent = parent
        self.x = x
        self.hists = {}
        #super(HistogramPanel, self).__init__(self, parent, **kwargs)
        PlotPanel.__init__( self, parent, **kwargs )
  
    def draw(self):
        colors = cq(['b','r','g'])
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
        self.subplot.clear()
        if self.x is not None:
            self.patches = []
            self.histograms = []
            color = colors.next()
            n, bins, hist = self.subplot.hist(self.x, 250, normed=True, fc=color, ec=color)
            self.patches.extend(hist)
            self.histograms.append(hist)
            self.subplot.set_xlabel(str(self.name), fontsize = 12)
            for group in self.hists.keys():
                print group
                if self.hists[group][1]:
                    color = colors.next()
                    n, bins, hist = self.subplot.hist(self.hists[group][0], 250, normed=True, fc=color, ec=color)
                    self.patches.extend(hist)
                    self.histograms.append(hist)
            sizes = [len(patch) for patch in self.histograms]
            sizes.insert(0,0)
            print sizes
            splits = cumsum(sizes)
            upper = len(splits)-1
            print len(self.patches)
            print splits
            self.subplot.patches = self.patches[splits[0]:splits[upper]]
        #super(HistogramPanel, self).set_resizeflag(True)
        self.Refresh()

    def plot_fit(self, x, mu, sd, counts):
        """Fit with normal mixture."""
        lines = []
        xx = linspace(min(x), max(x), 100)
        envelope= zeros(len(xx), 'd')
        total = sum(counts)
        for i, (loc, scale, count) in enumerate(zip(mu, sd, counts)):
            count /= total
            line = self.subplot.plot(xx, count*norm(loc=loc,scale=scale).pdf(xx), 'r--', linewidth=2)
            lines.append(line)
            envelope += count*norm(loc=loc,scale=scale).pdf(xx)
        line = self.subplot.plot(xx, envelope, 'r-', linewidth=2)
        lines.append(line)
        self.Refresh()
        
class cq(object): # the argument q is a list
   def __init__(self,q):
      self.q = q
   def __iter__(self):
      return self
   def next(self):
      self.q = self.q[1:] + [self.q[0]]
      return self.q[-1]

