import wx
import  wx.lib.scrolledpanel as scrolled


class orderedListDialog(wx.Dialog):
    def __init__(self,parent, list, title='Order Timecourse Data'):
        wx.Dialog.__init__(self, parent, -1, title)
        self.panel = scrolled.ScrolledPanel(self, -1)
        #self.panel = wx.ScrolledWindow(self, -1)
        num = len(list)
        self.items = list
        self.sizer = wx.BoxSizer(wx.VERTICAL) 
        
        self.panelsizer = wx.GridSizer(num+1,1,0,0)
        self.pluses = {}
        self.minuses = {}
        self.order = []
        self.lines = {}
        for index in range(len(self.items)):
            panel = wx.Panel(self.panel, -1)
            line = wx.BoxSizer(wx.HORIZONTAL)
            text = wx.StaticText(panel, -1, self.items[index])
            plus = wx.Button(panel, -1, '+')
            minus = wx.Button(panel, -1, '-')
            self.order.append( self.items[index])
            self.pluses[plus.GetId()] = self.items[index]
            self.minuses[minus.GetId()] = self.items[index]
            self.lines[self.items[index]] = panel
            
            self.Bind(wx.EVT_BUTTON, self.onPlus, plus)
            self.Bind(wx.EVT_BUTTON, self.onMinus, minus)
            
            line.Add(plus,0)
            line.Add(minus,0)
            line.Add(text,0)
            panel.SetSizer(line)
            self.panelsizer.Add(panel,0)
            
        
        self.panel.SetSizer(self.panelsizer)
        #self.panel.FitInside()
        #self.panel.SetScrollRate(1,1)
        self.panel.SetAutoLayout(1)
        self.panel.SetupScrolling(scroll_x=False)

        self.ok = wx.Button(self, wx.ID_OK) 
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.sizer.Add(self.ok,0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        
    def onPlus(self, evt):
        id = evt.GetId()
        item = self.pluses[id]
        line = self.lines[item]
        print 'move %s up one' % item

        index = self.order.index(item)
        #print index
        if index is not 0:
            if self.panelsizer.Remove(line):
                pos = self.panel.GetScrollPos(0)
                self.panel.Scroll(0,0)
                self.order.remove(item)
                self.order.insert(index-1, item)
                self.panelsizer.Insert(index-1, line)
                self.panelsizer.Layout()
                self.panel.Scroll(0,pos)
                
            #print self.order
        

    def onMinus(self, evt):
        id = evt.GetId()
        item = self.minuses[id]
        line = self.lines[item]
        print 'move %s down one' % item
        index = self.order.index(item)
        if index is not len(self.order)-1:
            if self.panelsizer.Remove(line):
                pos = self.panel.GetScrollPos(0)
                self.panel.Scroll(0,0)
                self.order.remove(item)
                self.order.insert(index+1, item)
                self.panelsizer.Insert(index+1, line)
                self.panelsizer.Layout()
                self.panel.Scroll(0,pos)
            #print self.order
            
            
if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = orderedListDialog(None, ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p'])
    if dlg.ShowModal() == wx.ID_OK:
        print dlg.order
                 


    