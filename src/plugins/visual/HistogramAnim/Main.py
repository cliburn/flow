"""Need type, Plot() and ModelUpdate()."""
import wx
import sys
import os
from wxPlots import PlotPanel
from numpy import cumsum, linspace, zeros
from VizFrame import VizFrame
from scipy.stats import norm
from orderedListFrame import orderedListDialog
import sets
import pylab


class HistogramAnimFrame(VizFrame):
    """frame for viewing histograms"""
    type = 'Animated Histogram'

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Histogram"):
        VizFrame.__init__(self, parent, id, pos, title)
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self,-1)

        self.widget = HistogramPanel(self,None)
        self.widget.draw()
        
        self.MenuBar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.MenuBar.Append(self.FileMenu, "File")
        self.SetMenuBar(self.MenuBar)
        export = self.FileMenu.Append(-1, "Export graphics")
        self.Bind(wx.EVT_MENU, self.OnExport, export)
        self.AddMenu = wx.Menu()
        
        self.RadioButtons(['none'])
        self.box.Add(self.panel,0,wx.EXPAND)
        self.box.Add(self.widget,1,wx.EXPAND)
        self.SetSizer(self.box)
        self.Show()
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
    
 
    
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
        label = self.radioX.GetItemLabel(x)
        xs = []
        for data in self.datas:
            fields = data.getAttr('fields')
            indx = fields.index(label)
            xs.append(data[:,indx])
            
        print xs
        self.widget.name = label
        self.widget.xs = xs
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
                self.UpdateHistogram(self.radioX.GetSelection())
            else:
                pass
        except AttributeError:
            pass

    def OnControlSwitch(self,event):
        self.UpdateHistogram(self.radioX.GetSelection())
        
    def OnIdle(self, event):
        self.widget.draw()
    
    def ModelUpdate(self,model):
        self.model = model
        self.datas = []
        choices = self.model.GetDataGroups()
        dialog = wx.MultiChoiceDialog(None, "Chose data to add to histogram", 'choices', choices)
        if dialog.ShowModal() == wx.ID_OK:
            list_dialog = orderedListDialog(self, [choices[i]  for i in dialog.GetSelections()])
            if list_dialog.ShowModal() == wx.ID_OK:
                print list_dialog.order
                headers = []
                for item in list_dialog.order:
                    self.model.SelectGroupByPath(item)
                    data = self.model.GetCurrentData()
                    headers.append(data.getAttr('fields'))
                    self.datas.append(data)
                    
                foo = intersect(headers)
                print foo
                self.RadioButtons(foo)
                self.Plot()
                    
        #self.data = self.model.GetCurrentData()
        #self.Plot()

class HistogramPanel(PlotPanel):
    """An example plotting panel. The only method that needs 
    overriding is the draw method"""
    def __init__(self,parent, x, name='', **kwargs):
        self.xs = x
        self.current = 0
        PlotPanel.__init__( self, parent, **kwargs )
  
    def draw(self):
        colors = cq(['b','r','g'])
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)
        self.subplot.clear()
        if self.xs is not None:
            maxed = max([max(x) for x in self.xs])
            self.patches = []
            self.histograms = []
            color = colors.next()
            n, bins, hist = self.subplot.hist(self.xs[self.current], 250, normed=True, fc=color, ec=color)
            self.patches.extend(hist)
            self.histograms.append(hist)
            self.subplot.set_xlabel(str(self.name), fontsize = 12)
            #self.subplot.xticks(pylab.arrange(maxed))
            sizes = [len(patch) for patch in self.histograms]
            sizes.insert(0,0)
            print sizes
            splits = cumsum(sizes)
            upper = len(splits)-1
            print len(self.patches)
            print splits
            self.subplot.patches = self.patches[splits[0]:splits[upper]]
            self.current = (self.current + 1) % len(self.xs)
            self.subplot.axis(xmax=maxed )
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

def intersect(items):
    try:
        test = sets.Set(items.pop())
    except IndexError:
        return sets.Set()
    for set in items:
        test = test.intersection(sets.Set(set))
    return list(test)
