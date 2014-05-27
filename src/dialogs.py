import os
import wx
import factory

class BlockWindow(wx.Panel): 
    def __init__(self, parent, ID=-1, label="", 
                 pos=wx.DefaultPosition, size=(350, 25)): 
        wx.Panel.__init__(self, parent, ID, pos, size, 
                          wx.RAISED_BORDER, label) 
        self.label = label 
        self.SetBackgroundColour("white") 
        self.SetMinSize(size) 
        self.Bind(wx.EVT_PAINT, self.OnPaint) 

    def OnPaint(self, evt): 
        sz = self.GetClientSize() 
        dc = wx.PaintDC(self) 
        w,h = dc.GetTextExtent(self.label) 
        dc.SetFont(self.GetFont()) 
        dc.DrawText(self.label, (sz.width-w)/2, (sz.height-h)/2) 

class RemoteProcessDialog(wx.Dialog):
    """Dialog box to specify server, data and job for processing."""
    def __init__(self, server, filename, data_path, data_shape, label="Remote process invocation"):
        wx.Dialog.__init__(self, None, -1, label)

        sizer = wx.BoxSizer(wx.VERTICAL)

        server_label = wx.StaticText(self, -1, 'Server URL')
        self.server_ctrl = wx.TextCtrl(self, -1, server, size=(300,-1))
        self.server_ctrl.SetInsertionPoint(0)
        
        user_label = wx.StaticText(self, -1, 'Username')
        self.user_ctrl = wx.TextCtrl(self, -1)
        
        password_label = wx.StaticText(self, -1, 'Password')
        self.password_ctrl = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)

        file_label = wx.StaticText(self, -1, 'File')
        self.file_ctrl = wx.TextCtrl(self, -1, filename)

        data_label = wx.StaticText(self, -1, 'Data')
        self.data_ctrl = wx.TextCtrl(self, -1, data_path)

        shape_label = wx.StaticText(self, -1, 'Dimensions')
        self.shape_ctrl = wx.TextCtrl(self, -1, str(data_shape))

        #  job_label = wx.StaticText(self, -1, 'Job Specification')
        self.job_ctrl = wx.TextCtrl(self, -1, 'Job specification file')
        job_button = wx.Button(self, -1, label="Browse")
        self.Bind(wx.EVT_BUTTON, self.OnClick, job_button)
        
        # layout
        fgs = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        fgs.AddGrowableCol(1) 

        fgs.Add(server_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.server_ctrl, 0, wx.EXPAND)

        fgs.Add(user_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.user_ctrl, 0, wx.EXPAND)

        fgs.Add(password_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.password_ctrl, 0, wx.EXPAND)

        fgs.Add(file_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.file_ctrl, 0, wx.EXPAND)

        fgs.Add(data_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.data_ctrl, 0, wx.EXPAND)

        fgs.Add(shape_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.shape_ctrl, 0, wx.EXPAND)

        fgs.Add(job_button, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.job_ctrl, 0, wx.EXPAND)

        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        
        btns = wx.StdDialogButtonSizer()
        btns.Add(okay)
        btns.Add(cancel)

        sizer.Add((20,20))
        sizer.Add(fgs, 0, wx.EXPAND|wx.ALL, border=25)
        sizer.Add((20,20))
        sizer.Add(btns, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=25)
        sizer.Add((20,20))

        sizer.Fit(self)
        self.SetSizer(sizer)
        

    def OnClick(self, event):
        """Opens file browser."""
        dlg = wx.FileDialog(self, 
                            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                            defaultDir='.',
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
        else:
            file = None
        dlg.Destroy()
        self.job_ctrl.SetValue(file)

class ParameterDialog(wx.Dialog):
    def __init__(self, params, data, desc=''):
        """params is a list of (name, validator, defaults) tuples."""
        wx.Dialog.__init__(self, None, -1, "Specify parameters")

        text = self.MakeStaticBoxSizer('Function', [desc])
        # create the entries
        labels = []
        entries = []
        for name, validator, default in params:
            labels.append(wx.StaticText(self, -1, name + ': '))
            entries.append(wx.TextCtrl(self, validator=factory.factory('validators', validator, data, name), value=default))
        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)

        # layout
        fgs = wx.FlexGridSizer(len(params)+1, 2, 5, 5)
        for label, entry in zip(labels, entries):
            fgs.Add(label, 0, wx.ALIGN_RIGHT)
            fgs.Add(entry, 0, wx.EXPAND)
        fgs.AddGrowableCol(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALIGN_CENTRE|wx.ALL, border=10)
        #for entry in entries:
        #    sizer.Add(entry)
        sizer.Add(fgs)
        btns = wx.StdDialogButtonSizer()
        btns.Add(okay)
        btns.Add(cancel)
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def MakeStaticBoxSizer(self, boxlabel, itemlabels): 
        box = wx.StaticBox(self, -1, boxlabel)   
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL) 
        for label in itemlabels:                     
            bw = BlockWindow(self, label=label)   
            sizer.Add(bw, 0, wx.EXPAND | wx.ALL, 2) 
        return sizer 

class ChoiceDialog(wx.Dialog):
    def __init__(self, choices, label ="Choose markers"):
        wx.Dialog.__init__(self, None, -1, label, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        # create the checklist box
        self.lb = wx.CheckListBox(self, -1, choices=choices)
        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)

        # check all by default
        for i in range(self.lb.GetCount()):
            self.lb.Check(i)

        # layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lb, 1, wx.EXPAND|wx.ALL, 5)
        btns = wx.StdDialogButtonSizer()
        btns.Add(okay)
        btns.Add(cancel)
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def GetSelections(self):
        selections = []
        for i in range(self.lb.GetCount()):
            if self.lb.IsChecked(i):
                selections.append(i)
        return selections

    def SetSelections(self, selections):
        for selection in selections:
            self.lb.Check(selection)

class DBInputDialog(wx.Dialog):
    def __init__(self, params, data, desc=''):
        """params is a list of (name, validator, defaults) tuples."""
        wx.Dialog.__init__(self, None, -1, "Specify parameters")

        text =wx.StaticText(self, -1, desc)
        # create the entries
        labels = []
        entries = []
        for name, validator, default in params:
            labels.append(wx.StaticText(self, -1, name + ': '))
            entries.append(wx.TextCtrl(self, validator=factory.factory('validators', validator, data, name), value=default))
        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)

        # layout
        fgs = wx.FlexGridSizer(len(params)+1, 2, 5, 5)
        for label, entry in zip(labels, entries):
            fgs.Add(label, 0, wx.ALIGN_RIGHT)
            fgs.Add(entry, 0, wx.EXPAND)
        fgs.AddGrowableCol(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALIGN_CENTRE|wx.ALL, border=10)
        sizer.Add(fgs)
        btns = wx.StdDialogButtonSizer()
        btns.Add(okay)
        btns.Add(cancel)
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

class SaveDialog(wx.Dialog):
    """Dialog to prompt users to save thier work"""
    def __init__(self):
        """init the dialog"""
        wx.Dialog.__init__(self, None, -1, "Save your work?", size = (300, 100))
        text = wx.StaticText(self, -1, "Save your work?")
        self.yesButton = wx.Button(self, wx.ID_YES, "Yes", pos = (15, 15))
        self.yesButton.SetDefault()
        buttonPos = (self.yesButton.GetPosition()[0]+self.yesButton.GetSize()[0]+5, 15)
        self.noButton = wx.Button(self, wx.ID_NO, "No", pos = buttonPos)
        buttonPos = (self.noButton.GetPosition()[0]+self.noButton.GetSize()[0]+5, 15)
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel", pos = buttonPos)
        self.Bind(wx.EVT_BUTTON, self.onButton, self.yesButton)
        self.Bind(wx.EVT_BUTTON, self.onButton, self.noButton)

    def onButton(self,event):
        """handle button events to end dialog"""
        if event.GetId() == self.yesButton.GetId():
            self.EndModal(wx.ID_YES)
        elif event.GetId() == self.noButton.GetId():
            self.EndModal(wx.ID_NO)
            
