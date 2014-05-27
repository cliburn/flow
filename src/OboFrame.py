"""Crude attempt to parse OBO file."""
import networkx as nx
import wx
import wx.gizmos as gizmos

import re
instr = re.compile(r'"(.*?)"')

class Cell(object):
    """Storage for parsing cell ontology obo entry"""
    def __init__(self, name):
        self.name = name
        self.definition = ''
        self.synonyms = []

    def __str__(self):
        return self.name

class OboTreeFrame(wx.Frame):
    """
    Build window to allow selecting of ontology item for field name
    """
    def __init__(self, model, parent, id = -1):
        """
        OboTreeFrame(parent = wx.windowID, id (=-1) = wx.windowId)
        """
        wx.Frame.__init__(self, parent, id, 'Rename Z labels')
        self.group = model.GetCurrentGroup()
        self.z = model.GetCurrentZ()
        self.values = model.GetZLabels(self.z)
        self.model = model
        
        self.g = nx.XDiGraph()
        self.adict = {}

        # create status bar
        self.CreateStatusBar()
        
        # make the widgets ...
        self.panel = wx.Panel(self, -1)
        self.chooserpanel = wx.Panel(self, -1)
        self.inputpanel = wx.Panel(self, -1)
        self.chooserlabel = wx.StaticText(self.chooserpanel, -1, "Current Label: ")
        self.chooser = wx.Choice(self.chooserpanel, -1, choices=self.values)
        self.chooser.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self.chooser)
        
        root_id, root_name = self.populateG(self.model.obofile)
        
        self.textprompt = wx.StaticText(self.inputpanel, -1, "Change Name To: ")
        self.text = wx.TextCtrl(self.inputpanel, -1,
                                self.chooser.GetStringSelection(), 
                                size=(-1, -1))
        self.text.SetInsertionPoint(0)
        #self.text.WriteText(self.chooser.GetStringSelection())

        self.change = wx.Button(self.inputpanel, wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON, self.OnApply, self.change)
        
        self.ok = wx.Button(self.panel, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.ok)
        
        self.cancel = wx.Button(self.panel, wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
        
        self.tree = wx.TreeCtrl(self.panel, -1, 
                                style = wx.TR_DEFAULT_STYLE | wx.NO_BORDER)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeActivated, self.tree)
        
        self.root = self.tree.AddRoot(root_name)
        
        self.print_tree(self.g, root_id, self.adict, self.root)
        self.tree.Expand(self.root)
        panelsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        
        choosersizer = wx.BoxSizer(wx.HORIZONTAL)
        choosersizer.Add(self.chooserlabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        choosersizer.Add(self.chooser, 1, wx.EXPAND)
        self.chooserpanel.SetSizer(choosersizer)
        
        textsizer = wx.BoxSizer(wx.HORIZONTAL)
        textsizer.Add(self.textprompt, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        textsizer.Add(self.text, 1, wx.EXPAND)
        textsizer.Add(self.change, 0)
        self.inputpanel.SetSizer(textsizer)
        
        mainsizer.Add(self.chooserpanel, 0, wx.EXPAND)
        mainsizer.Add(self.inputpanel, 0, wx.EXPAND)
        mainsizer.Add(self.tree, 1, wx.EXPAND)
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(self.ok)
        btns.AddButton(self.cancel)
        btns.Realize()
        mainsizer.Add(btns, 0, wx.EXPAND|wx.ALL)
        self.panel.SetSizer(mainsizer)
        
        
        panelsizer.Add(self.panel, 1, wx.EXPAND)
        
        
        self.SetSizer(panelsizer)
        panelsizer.Fit(self)
        
        
    def populateG(self, filename):
        """
        build digraph
        populateG(filename = string)
        """
        # clear stuff first - may reuse
        self.g = nx.XDiGraph()
        self.adict = {}

        obo = open(filename).read().split('[Term]')

        # first entry is root of graph
        for line in obo[1].split('\n'):
            items = [s.strip() for s in line.split(': ')]
            if items[0] == 'id':
                root_id = items[1].split('!')[0].strip()
            if items[0] == 'name':
                root_name = items[1]
        
        for term in obo:
            lines = [line for line in term.split('\n') if line.strip() != '']

            for line in lines:
                items = [s.strip() for s in line.split(': ')]
                if items[0] == 'id':
                    cls = items[1].split('!')[0].strip()
                    self.g.add_node(cls)
                    cur_id = cls
                elif items[0] == 'is_a':
                    cls = items[1].split('!')[0].strip()
                    self.g.add_node(cls)
                    # cur_id exists because id field is first in every term
                    self.g.add_edge(cls, cur_id) 
                elif items[0] == 'name':
                    self.adict[cls] = Cell(items[1])
                elif items[0] == 'def':
                    s = instr.search(items[1])
                    if s:
                        self.adict[cls].definition = s.group(1)
                elif items[0] == 'exact_synonym':
                    s = instr.search(items[1])
                    if s:
                        self.adict[cls].synonyms.append(s.group(1))
        return root_id, root_name
               
    def print_tree(self, g, n, names, parent):
        """
        walk the tree recursivly and see if any populate tree control with children
        print_tree(g = nx.digraph, n = string, names = dict, parent = wx.treeitem)
        """
        cell = names[n]
        item = self.tree.AppendItem(parent, cell.name)
        self.tree.SetItemPyData(item, cell.definition)
        for succ in g.successors_iter(n):
            self.print_tree(g, succ, names, item)
        self.tree.Expand(item)

    def OnApply(self, event):
        """
        apply button event handler
        OnApply(event = wx.event)
        """
        current = self.chooser.GetSelection()
        self.chooser.SetString(current, self.text.GetLineText(0) )
        self.chooser.Refresh()
 
    def OnOK(self, event):
        """
        ok button event handler
        OnOK(event = wx.event)
        """
        self.OnApply(event)
        newValues = []
        for i in range(self.chooser.GetCount()):
            newValues.append(self.chooser.GetString(i))
        print newValues
        self.model.SetZLabels(self.z, newValues)
        self.Destroy()
    
    def OnCancel(self, event):
        """
        cancel event handler
        OnCancel(event = wx.event)
        """
        #print "closing via cancel"
        self.Destroy()
        
    def OnChoice(self, event):
        """
        event to handle changes from the chooser
        OnChoise(event = wx.event)
        """
        self.text.Clear()
        changed = self.chooser.GetStringSelection()
        self.text.SetInsertionPoint(0)
        self.text.WriteText(changed)
        
    def OnTreeActivated(self,event):
        """
        updates text box with selected item in tree
        OnTreeActivated(event = wx.event)
        """
        text = self.tree.GetItemText(event.GetItem())
        self.text.Clear()
        self.text.SetInsertionPoint(0)
        self.text.WriteText(text)
        self.SetStatusText(self.tree.GetItemPyData(event.GetItem()))
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    values = ['Color 1', 'color 2', 'color 3']
    frame = OboTreeFrame(values = values, parent=None, id=-1)
    frame.Show()
    app.MainLoop()
    
    
#    adict = {}
#    obo = open('obo/cell.obo').read().split('[Term]')
#
#
#
#    # CL:0000063 is the id for 'cell by histology'
#    root = 'CL:0000063'
#    print_tree(g, root, adict)
#                
                
