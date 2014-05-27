import wx
import wx.grid
from wxPlots import PlotPanel
import pylab
import numpy
from numpy.linalg import solve
from Model import FlowModel



class CompensationFrame(wx.Frame):
    def __init__(self, model, matrix=None):
        self.model=model
        self.data = model.GetCurrentData()
        self.points = self.data[:,:]
        self.OrigPoints = self.points[:,:]
        self.matrix = matrix
        wx.Frame.__init__(self, None, -1, "Compensating", style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER )
        self.panel = wx.Panel(self, -1, size = self.GetSize() )
        
        #Object in the panel/frame
        instruct = wx.StaticText(self.panel, -1, "Instructions")
        self.graphs = GraphingPanel(self.panel, -1, self.data[:,0],self.data[:,0])
        self.grid = wx.grid.Grid(self.panel)
        
        try:
            self.headers = self.data.getAttr('fields')[:]
        except AttributeError:
            self.headers = None
            
        self.origSize=len(self.headers)
        self.skips = []
        newheaders = self.headers[:]
        for a,b in enumerate(self.headers):
            print a, b
            if b.startswith('FSC') or b.startswith('SSC') or b.startswith('Time'):
                print 'throwing out column ' + b
                newheaders.remove(b)
            else:
               self.skips.append(a)
        print self.skips
        self.headers = newheaders
        
        self.gridSize = len(self.headers)
        self.grid.CreateGrid(self.gridSize,self.gridSize)
        #self.grid.CreateGrid(4,4)
        rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        self.gridDefaultColor = self.grid.GetCellBackgroundColour(0,0)
        self.grid.SetDefaultEditor(wx.grid.GridCellFloatEditor())
        self.pos = None
        for i in range(self.gridSize):
            self.grid.SetRowLabelValue(i,self.headers[i])
            self.grid.SetColLabelValue(i,self.headers[i])
            for j in range(self.gridSize):
                if i == j :
                    self.grid.SetCellBackgroundColour(i,j, wx.Colour(*rgbtuple))
                    self.grid.SetReadOnly(i,j, isReadOnly=True)
                    self.grid.SetCellValue(i,j, '1')
                else:
                    self.grid.SetCellValue(i,j, '0')
                if self.matrix is not None:
                    self.grid.SetCellValue(i,j, str(self.matrix[i,j]))
                
        self.grid.AutoSize()
        self.grid.Bind(wx.EVT_SIZE, self.OnGridSize)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnCellSelect, self.grid)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnEdit)
        
        self.okBtn = wx.Button(self.panel, id=wx.ID_OK)
        self.cancelBtn = wx.Button(self.panel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnOkay, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        mainSizer.Add(instruct,0,wx.EXPAND)
        
        middleSizer.Add(self.graphs,1,wx.EXPAND)
        middleSizer.Add(self.grid,0)
        
        mainSizer.Add(middleSizer,1, wx.EXPAND)
        
        btnSizer.Add((10,10),1)
        btnSizer.Add(self.cancelBtn)
        btnSizer.Add((10,10))
        btnSizer.Add(self.okBtn)
        btnSizer.Add((10,10))
        mainSizer.Add(btnSizer, 0, wx.EXPAND)
        
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Layout()
        
        
    def OnGridSize(self, event):
        #self.grid.AutoSize()
        size = self.grid.GetBestSize()
        self.grid.SetSize(size)
        
    def OnOkay(self, event):
        """
        do aproprate action on okay button press
        """
        # need to do stuff here
        self.model.updateHDF("Compensated Data", self.points, self.data)
                          
        self.Destroy()
        
    def OnCancel(self, event):
        """
        cancel button handler
        """
        self.Destroy()
        
    def OnCellSelect(self, event):
        """
        handle selecting cells so the oposite cell is highlighted
        """
        if self.pos is not None:
            if self.pos[0] != self.pos[1]:
                self.grid.SetCellBackgroundColour(self.pos[1], self.pos[0], self.gridDefaultColor )

        if event.Selecting():
            
            self.pos = [event.GetRow(), event.GetCol()]
            if self.pos[0] != self.pos[1]:
                self.grid.SetCellBackgroundColour(self.pos[1], self.pos[0], wx.Colour(*(255,128,128)))
            self.grid.Refresh()
            self.graphs.x = self.points[:,self.skips[self.pos[0]]]
            self.graphs.y = self.points[:,self.skips[self.pos[1]]]
            self.graphs.draw()

            
        event.Skip()
        
    def OnEdit(self, event):
#        print "Setting Grid Cursor"
#        self.grid.SetGridCursor(event.GetRow(), event.GetCol())
        self.Compensate()
        #pos = [event.GetRow(), event.GetCol()]
        #self.grid.SelectBlock(pos[0],pos[1],pos[0],pos[1])
        #self.grid.SetGridCursor(pos[0],pos[1])
        event.Skip()
    
    def Compensate(self):
        comp = numpy.zeros((self.origSize, self.origSize))
        for i in xrange(self.origSize):
            comp[i,i]=1
        
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                comp[self.skips[i],self.skips[j]] = float(self.grid.GetCellValue(i,j))
#        indices = [data.attrs.fields.index(data.attrs.NtoS[m])
#                       for m in self.headers]
#        observed = array([data[:,i] for i in indices])
        self.points = solve(comp, self.OrigPoints.T).T  ## todo fix matix sizes.
        

class GraphingPanel(PlotPanel):
    def __init__(self,parent, id, x,y,**kwargs):
         self.x = x
         self.y = y
         PlotPanel.__init__( self, parent, **kwargs )
         # this really doesn't seem to speed things up much...
#         speed = 10000
#         if len(self.x) > speed:
#             stride = len(self.x)/speed
#         else:
#             stride = 1
#        
#         self.x = self.x[:speed*stride:stride]
#         self.y = self.y[:speed*stride:stride]
         
    def draw(self):
         if not hasattr(self, 'subplot'):
             self.subplot = self.figure.add_subplot(111)
         self.subplot.clear()
         bins = 250
         if len(self.x) > 10000:
             stride = len(self.x)/10000
         else:
            stride = 1
        
         self.x = self.x[:10000*stride:stride]
         self.y = self.y[:10000*stride:stride]

         z, xedge, yedge = numpy.histogram2d(self.y, self.x, bins=[bins, bins], 
                                    range=[(numpy.min(self.y), numpy.max(self.y)),
                                           (numpy.min(self.x), numpy.max(self.x))])
         #xint = map(int, (self.x - numpy.min(self.x))/(numpy.max(self.x)-numpy.min(self.x))*(bins-1))
         #yint = map(int, (self.y - numpy.min(self.y))/(numpy.max(self.y)-numpy.min(self.y))*(bins-1))
         xfrac, xint = numpy.modf((self.x - numpy.min(self.x))/
                         (numpy.max(self.x)-numpy.min(self.x))*(bins-1))
         yfrac, yint = numpy.modf((self.y - numpy.min(self.y))/
                         (numpy.max(self.y)-numpy.min(self.y))*(bins-1))
         #zvals = numpy.array([z[_y, _x] for _x, _y in zip(xint, yint)])
         zvals = numpy.zeros(len(xint), 'd')
         for i, (_x, _y, _xf, _yf) in enumerate(zip(xint, yint, xfrac, yfrac)):
            q11 = z[_y, _x]
            if _xf:
                q12 = z[_y, _x+1]
            else:
                q12 = 0
            if _yf:
                q21 = z[_y+1, _x]
            else:
                q21 = 0
            if _xf and _yf:
                q22 = z[_y+1, _x+1]
            else:
                q22 = 0

            zvals[i] = q11*(1-_xf)*(1-_yf) + q21*(1-_xf)*(_yf) + \
                       q12*(_xf)*(1-_yf) + q22*(_xf)*(_yf)
         
         self.subplot.scatter(self.x,self.y,s=1, c=zvals, edgecolors='none' )
         self.Refresh()
         
      
if __name__ == '__main__':
    app = wx.PySimpleApp()
    import tables
    foo = tables.openFile('../data/3FITC_4PE_004.h5')
    data = foo.getNode('/3FITC_4PE_004/data')

    bar = CompensationFrame(data)
    bar.Show()
    app.MainLoop()