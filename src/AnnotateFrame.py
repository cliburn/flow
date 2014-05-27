import wx
from numpy import array

class annotateFrame(wx.Frame):
    def __init__(self, group, model, group_name = 'default', annotations = None):
        wx.Frame.__init__(self, None, -1, "Annotations for " + group_name,style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER )
        self.panel = wx.ScrolledWindow(self, -1, size = self.GetSize() , style = wx.DEFAULT | wx.VSCROLL)
        self.panel.SetScrollRate(5,5)
        #self.textBox = wx.TextCtrl(self.panel, -1, txt, style= wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
        self.okBtn = wx.Button(self.panel, id=wx.ID_OK)
        self.cancelBtn = wx.Button(self.panel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnOkay, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        
        self.group = group
        self.model = model
        
        self.annotations = []
        self.notebox = wx.FlexGridSizer(2,2, 5,5)
        self.notebox.Add(wx.StaticText(self.panel, -1, 'Name'))
        self.notebox.Add(wx.StaticText(self.panel, -1, 'Value'))
        self.notebox.AddGrowableCol(0,1)
        self.notebox.AddGrowableCol(1,1)
        if annotations is not None:
            for note in annotations:
                self.notebox.SetRows(self.notebox.GetRows()+1)
                name = wx.TextCtrl(self.panel, -1, note[0], style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
                value = wx.TextCtrl(self.panel, -1, note[1], style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
                self.notebox.Add(name, 1, wx.EXPAND)
                self.notebox.Add(value, 1, wx.EXPAND)
                self.annotations.append((name,value))
                self.Bind(wx.EVT_TEXT, self.OnNotes, name)
                self.Bind(wx.EVT_TEXT, self.OnNotes, value)
            
        name = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
        value = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
        self.notebox.Add(name, 1 , wx.EXPAND)
        self.notebox.Add(value, 1, wx.EXPAND)
        self.Bind(wx.EVT_TEXT, self.OnNotes, name)
        self.Bind(wx.EVT_TEXT, self.OnNotes, value)
        self.annotations.append((name,value))
            
            
        #layout
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        #mainsizer.Add(self.textBox,1,wx.EXPAND)
        self.mainsizer.Add(self.notebox, 1, wx.EXPAND)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.Add((10,10),1)
        btnsizer.Add(self.cancelBtn)
        btnsizer.Add((10,10))
        btnsizer.Add(self.okBtn)
        btnsizer.Add((10,10))
        self.mainsizer.Add(btnsizer, 0, wx.EXPAND)
        self.panel.SetSizer(self.mainsizer)
        self.mainsizer.Fit(self)
        self.panel.FitInside()
        
    def OnNotes(self, event):
        full = True
        for note in self.annotations:
            if not note[0].GetValue():
                full = False
            if not note[1].GetValue():
                full = False
        if full:
            name = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
            value = wx.TextCtrl(self.panel, -1, '', style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL)
            self.notebox.SetRows(self.notebox.GetRows()+1)
            self.notebox.Add(name,1,wx.EXPAND)
            self.notebox.Add(value,1,wx.EXPAND)
            self.annotations.append((name,value))
            self.Bind(wx.EVT_TEXT, self.OnNotes, name)
            self.Bind(wx.EVT_TEXT, self.OnNotes, value)
            self.notebox.Layout()
            self.mainsizer.Layout()
            self.panel.FitInside()
            
    def OnOkay(self, event):
        """
        do aproprate action on okay button press
        """
        # need to do stuff here
        new = []
        for note in self.annotations:
            new.append(( note[0].GetValue().encode('utf8'), note[1].GetValue().encode('utf8')))
        #print new
        annote = array(filter(lambda x: x != ('',''), new))
        self.model.NewArray('annotation', annote, parent=self.group, overwrite=True)
        #self.model.hdf5.createArray(self.group, 'annotation', annote)
                          
        self.Destroy()
        
    def OnCancel(self, event):
        """
        cancel button handler
        """
        self.Destroy()
        
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    bar = annotateFrame('bar', 'test')
    bar.Show()
    app.MainLoop()
