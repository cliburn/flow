import wx
import wx.grid
import numpy

class SpillFrame(wx.Frame):
    def __init__(self, spill, markers):
        wx.Frame.__init__(self, None, -1, "Spillover matrix", style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER )
        
        grid = wx.grid.Grid(self)
        table = Table(spill, markers)
        grid.SetTable(table, True)

class EditFrame(wx.Frame):
    def __init__(self,data):
        wx.Frame.__init__(self,None,-1, "Viewing " + str(data), style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER )
        
        grid = wx.grid.Grid(self)
        try:
            headers = data.getAttr('fields')
        except AttributeError:
            headers = None
            
        table = Table(data, headers)
        grid.SetTable(table, True)
        
class Table(wx.grid.PyGridTableBase):
    def __init__(self, data, headers):
        wx.grid.PyGridTableBase.__init__(self)
        self._data = data
        
        datacpy = data[:]
        if type(datacpy) is list or len(datacpy.shape)==1:
            self.rows = len(datacpy)
            self.cols = 1
        else:
            self.rows, self.cols = datacpy.shape[0], datacpy.shape[1]

        if headers is not None:
            self.headers = headers
        else:
            self.headers = map(str, range(self.cols))
        
        self.data = {}
        if type(datacpy) is list or len(datacpy.shape)==1:
            for row in range(self.rows):
                self.data[(row,0)] = datacpy[row]
        else:
            for row in range(self.rows):
                for col in range(self.cols):
                    self.data[(row,col)] = datacpy[row,col]
        del datacpy
    
    def GetNumberCols(self):
        return self.cols
    
    def GetNumberRows(self):
        return self.rows
    
    def GetValue(self, row, col):
        value = self.data.get((row,col))
        if value is not None:
            return value
        else:
            return ''

    def GetColLabelValue(self, col):
        return self.headers[col]
    
    def IsEmptryCell(self, row, col):
        return self.data.get((row,col)) is not None
    
    def SetValue(self, row, col, value):
        self.data[(row,col)] = value
        self._data[row, col] = value
        
