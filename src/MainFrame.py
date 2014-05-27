import wx
import os
from my_io import Io
from VizFrame import VizFrame
from EditTable import EditFrame, Table
from dialogs import ParameterDialog, ChoiceDialog, RemoteProcessDialog
from numpy import array, where, greater, log10, log, clip, take, argsort, arcsinh, min, max, savetxt, loadtxt
from numpy.random import shuffle, randint, get_state
import transforms
from OboFrame import OboTreeFrame
from AnnotateFrame import annotateFrame
import sys
from net_wrapper import connect

class MainFrame(VizFrame):
    """Main user interface frame includes the control panel"""
    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Flow Control Window"):
        """creates main frame for user interface"""
        VizFrame.__init__(self, parent, id, pos, title)
        self.sp = wx.SplitterWindow(self, -1)
        self.p1 = wx.Panel(self.sp, -1)
        self.p2 = wx.Panel(self.sp, -1)
        self.tree = wx.TreeCtrl(self.p1, -1, wx.DefaultPosition, wx.DefaultSize,
                                wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS)
        self.tree.SetDimensions(0, 0, 100, 100)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeEdit, self.tree)
        self.root = self.tree.AddRoot('root')

        self.log = wx.TextCtrl(self.p2, -1, "",
                                       style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY, size=(200,100))
        # current server URL
        self.server = 'http://localhost/'

        menubar = wx.MenuBar()


        transforms = {}
        transforms['clip'] = (self.OnClip, "Clip transform")
        transforms['scale'] = (self.OnScale, "Scale transform")
        transforms['normal_scale'] = (self.OnNormalScale, "Normal scale transform")
        transforms['linear'] = (self.OnLinear, "Linear transform")
        transforms['quadratic'] = (self.OnQuadratic, "Quadtratic transform")
        transforms['log'] = (self.OnLog, "Log10 transform")
        transforms['logn'] = (self.OnLogn, "LogN transform")
        transforms['biexponential'] = (self.OnBiexponential, "Biexponential transform")
        transforms['logicle'] = (self.OnLogicle, "Logicle transform")
        transforms['heyperlog'] = (self.OnHyperlog, "Hyperlog transform")
        transforms['arcsinh'] = (self.OnArcsinh, "Arcsinh transform")
        # transform menu
        self.transformMenu = wx.Menu()
        for i in transforms.keys():
            menuitem = self.transformMenu.Append(-1, transforms[i][1])
            self.Bind(wx.EVT_MENU, transforms[i][0], menuitem)

        # filter menu
        self.filterMenu = wx.Menu()
        self.channels = self.filterMenu.Append(-1, "Sub-Sample by channel")
        self.filterMenu.AppendSeparator()
        self.events_index = self.filterMenu.Append(-1, "Sub-Sample events: index")
        self.events_random = self.filterMenu.Append(-1, "Sub-Sample events: random choice without replacement")
        self.events_replace = self.filterMenu.Append(-1, "Sub-Sample events: random choice with replacement")

        # bind filter menuitems
        self.Bind(wx.EVT_MENU, self.OnChannels, self.channels)
        self.Bind(wx.EVT_MENU, self.OnEventsIndex, self.events_index)
        self.Bind(wx.EVT_MENU, self.OnEventsRandom, self.events_random)
        self.Bind(wx.EVT_MENU, self.OnEventsReplace, self.events_replace)

        # ontology menu
        self.ontologyMenu = wx.Menu()
        loadOntology = self.ontologyMenu.Append(-1, "Load OBO file")
        self.Bind(wx.EVT_MENU, self.OnLoadOntology, loadOntology)

        # remote process menu
        self.remoteProcessMenu = wx.Menu()
        submit_job = self.remoteProcessMenu.Append(-1, "Submit job to remote process")
        submit_batch = self.remoteProcessMenu.Append(-1, "Submit batch jobs to remote process")
        self.Bind(wx.EVT_MENU, self.OnSubmitJob, submit_job)
        self.Bind(wx.EVT_MENU, self.OnSubmitBatch, submit_batch)

        self.SetMenuBar(menubar)
        #statusbar = self.CreateStatusBar()
        # createEdit needs to be called before CreatePopup
        # to ensure menu's wx.IDs are consistent
        self.edit = self.CreateEdit()
        self.popup = self.CreatePopup()
        self.zPopMenuItem = None
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnShowPopup, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDisplayItem, self.tree)

        # default dir for OBO files
        self.defaultOBOdir = "."
        self.exportDir = self.io.defaultDir.replace('results','data')

        # flag for saved
    def DoLayout(self):
        # layout code
        self.box = wx.BoxSizer(wx.VERTICAL)

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.VERTICAL)

        panelsizer.Add(self.sp, 1, wx.EXPAND, 0)
        box1.Add(self.tree, 1, wx.EXPAND, 0)
        box2.Add(self.log,1, wx.EXPAND)

        self.p1.SetSizer(box1)
        self.p2.SetSizer(box2)
        self.SetSizer(panelsizer)
        self.box.Layout()
        self.Layout()

        self.sp.SplitVertically(self.p1, self.p2)
        self.sp.SetMinimumPaneSize(20)

    # Ontology
    def OnLoadOntology(self, event):
        """Load an ontology in OBO format"""
        dlg = wx.FileDialog(self,
                            wildcard="OBO files (*.obo)|*.obo|All files (*.*)|*.*",
                            defaultDir=self.defaultOBOdir,
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.defaultOBOdir = os.path.split(file)[0]
            self.model.obofile = file

        dlg.Destroy()

    # Remote process
    def OnSubmitJob(self, event):
        """Job submission dialog."""
        if self.model.ready:
            _data = self.model.GetCurrentData()
            data = _data[:]
            data_path = _data._v_pathname
            filename = self.model.savedAs
        else:
            wx.MessageBox("No data found")
            return

        dlg = RemoteProcessDialog(self.server, filename, data_path, data.shape)
        if dlg.ShowModal() == wx.ID_OK:
            self.server = dlg.server_ctrl.GetValue()
            self.user = dlg.user_ctrl.GetValue()
            self.password = dlg.password_ctrl.GetValue()
            self.filename = dlg.file_ctrl.GetValue()
            self.data = dlg.data_ctrl.GetValue()
            self.job = dlg.job_ctrl.GetValue()

            print self.server, self.user, self.password, self.filename, self.data, self.job
            session = connect(self.server, self.user, self.password)
            session.send_data(self.data)
            #TODO add sending source file name for use later
            #session.send_filename(self.filename) #NOT IMPLEMENTED
            job_def = parsejob(self.job)
            print job_def
            session.send_job(job_def)
        dlg.Destroy()


    def OnSubmitBatch(self, event):
        """Batch job submission dialog."""
        pass
#         if self.model.ready:
#             data = self.model.GetCurrentData()[:]
#         else:
#             wx.MessageBox("No data found")
#             return

#         dlg = RemoteProcessDialog(self.model.server)
#         if dlg.ShowModal() == wx.ID_OK:
#             job = dlg.job
#             self.model.server = dlg.server_ctrl.GetValue()
#             print data.shape, job, self.model.server

#         dlg.Destroy()


    # Filters
    def OnChannels(self, event):
        if self.model.ready:
            cs = self.model.GetCurrentData().getAttr('fields')
        else:
            cs = []
        dlg = ChoiceDialog(cs)
        if dlg.ShowModal() == wx.ID_OK:
            indices = dlg.GetSelections()
            name = self.model.GetCurrentGroup()._v_pathname
            self.model.FilterOnCols('FilterOnCols', indices)
            self.model.AddHistory(('FilterOnCols', [name, indices]))
        dlg.Destroy()

    def OnEventsIndex(self, event):
        data = array(self.model.GetCurrentData()[:])
        n = data.shape[0]

        inputs = {}
        dlg = ParameterDialog([('start', 'IntValidator', str(0)),
                               ('stop', 'IntValidator', str(n)),
                               ('stride', 'IntValidator', str(1))],
                              inputs,
                              'Returns data[start:stop:stride, :]')
        if dlg.ShowModal() == wx.ID_OK:
            indices = range(inputs['start'], inputs['stop'], inputs['stride'])
            name = self.model.GetCurrentGroup()._v_pathname
            self.model.FilterOnRows('SampleOnEventsIndex', indices)
            self.model.AddHistory(('SampleOnRows', [name, inputs]))
        dlg.Destroy()

    def OnEventsRandom(self, event):
        data = array(self.model.GetCurrentData()[:])
        n = data.shape[0]

        inputs = {}
        dlg = ParameterDialog([('n', 'IntValidator', str(n))],
                              inputs,
                              'Random choice of n events without replacement')
        if dlg.ShowModal() == wx.ID_OK:
            indices = range(n)
            shuffle(indices)
            indices = indices[:inputs['n']]
            name = self.model.GetCurrentGroup()._v_pathname
            self.model.FilterOnRows('SampleOnEventsRandom', indices)
            self.model.AddHistory(('SampleOnRows', [name, inputs, ('state', get_state())]))
        dlg.Destroy()

    def OnEventsReplace(self, event):
        data = array(self.model.GetCurrentData()[:])
        n = data.shape[0]

        inputs = {}
        dlg = ParameterDialog([('n', 'IntValidator', str(n))],
                              inputs,
                              'Random choice of n events with replacement')
        if dlg.ShowModal() == wx.ID_OK:
            indices = randint(0, n, inputs['n'])
            name = self.model.GetCurrentGroup()._v_pathname
            self.model.FilterOnRows('SampleOnEventsReplace', indices)
            self.model.AddHistory(('SampleOnRows', [name, inputs, ('state', get_state())]))
        dlg.Destroy()

    # Transforms
    def GetIndices(self, dlg2):
        inputs = {}
        if self.model.ready:
            cs = self.model.GetCurrentData().getAttr('fields')
        else:
            cs = []

        dlg = ChoiceDialog(cs)
        if dlg.ShowModal() == wx.ID_OK:
            indices = dlg.GetSelections()
            if dlg2.ShowModal() == wx.ID_OK:
                pass
            dlg2.Destroy()
        dlg.Destroy()
        return indices

    def OnClip(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('lower', 'FloatValidator', str(0.0)),
                                ('upper', 'FloatValidator', str(1024.0))],
                               inputs,
                               'f(x) = clip(x, lower, upper)')
        indices = self.GetIndices(dlg2)
        self.model.ClipTransform(indices, inputs)

    def OnScale(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('lower', 'FloatValidator', str(0.0)),
                                ('upper', 'FloatValidator', str(1024.0))],
                               inputs,
                               'f(x) = lower + (upper-lower)*(x - min(x))/(max(x)-min(x))')
        indices = self.GetIndices(dlg2)
        self.model.ScaleTransform(indices, inputs)

    def OnNormalScale(self, event):
        inputs = {}
        dlg2 = ParameterDialog([],
                               inputs,
                               'f(x) = (x - mean(x))/std(x)')
        indices = self.GetIndices(dlg2)
        self.model.NormalScaleTransform(indices, inputs)

    def OnLinear(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('a', 'FloatValidator', str(0)),
                                ('b', 'FloatValidator', str(1))],
                               inputs,
                               'f(x) = a + b*x')
        indices = self.GetIndices(dlg2)
        self.model.LinearTransform(indices, inputs)

    def OnQuadratic(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('a', 'FloatValidator', str(0)),
                                ('b', 'FloatValidator', str(1)),
                                ('c', 'FloatValidator', str(0))],
                               inputs,
                               'f(x) = a*x^2 + b*x + c')
        indices = self.GetIndices(dlg2)
        self.model.QuadraticTransform(indices, inputs)

    def OnLog(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('l', 'FloatValidator', str(1)),
                                ('r', 'FloatValidator', str(1)),
                                ('d', 'FloatValidator', str(1))],
                               inputs,
                               'f(x) = r/d * log10(x) for x>l, 0 otherwise')
        indices = self.GetIndices(dlg2)
        self.model.LogTransform(indices, inputs)

    def OnLogn(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('l', 'FloatValidator', str(1)),
                                ('r', 'FloatValidator', str(1)),
                                ('d', 'FloatValidator', str(1))],
                               inputs,
                               'f(x) = r/d * log(x) for x>l, 0 otherwise')
        indices = self.GetIndices(dlg2)
        self.model.LognTransform(indices, inputs)

    def OnBiexponential(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('a', 'FloatValidator', str(0.5)),
                                ('b', 'FloatValidator', str(1.0)),
                                ('c', 'FloatValidator', str(0.5)),
                                ('d', 'FloatValidator', str(1.0)),
                                ('f', 'FloatValidator', str(0))],
                               inputs,
                               'finv(x) = a*exp(b*x) - c*exp(d*x) + f')
        indices = self.GetIndices(dlg2)
        self.model.BiexponentialTransform(indices, inputs)

    def OnLogicle(self, event):
        inputs = {}
        data = array(self.model.GetCurrentData()[:])
        T = 262144
        # find r as 5th percentile of negative values for each column
        r = 0.05
        dlg2 = ParameterDialog([('T', 'FloatValidator', str(T)),
                                ('M', 'FloatValidator', str(4.5)),
                                ('r', 'FloatValidator', str(r))],
                               inputs,
                               'finv(x) = T*exp(-(m-w))*(exp(x-w)-p^2*exp(-(x-w)/p)+p^2-1')
        indices = self.GetIndices(dlg2)
        self.model.LogicleTransform(indices, inputs)

    def OnHyperlog(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('b', 'FloatValidator', str(100.0)),
                                ('d', 'FloatValidator', str(5.0)),
                                ('r', 'FloatValidator', str(1024.0))],
                               inputs,
                               'finv(x) = sgn(x)*10^(x*sgn(x)*d/r) + b*(d/r)*y - sgn(x)')
        indices = self.GetIndices(dlg2)
        self.model.HyperlogTransform(indices, inputs)

    def OnArcsinh(self, event):
        inputs = {}
        dlg2 = ParameterDialog([('a', 'FloatValidator', str(1.0)),
                                ('b', 'FloatValidator', str(1.0)),
                                ('c', 'FloatValidator', str(0.0))],
                               inputs,
                               'x = arcsinh(a+b*x) + c')
        indices = self.GetIndices(dlg2)
        self.model.ArcsinhTransform(indices, inputs)


    def ModelUpdate(self, model):
        VizFrame.ModelUpdate(self, model)
        self.io.ModelUpdate(self.model)
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot('root')
        self.treeItems = []
        self.treeItems.append(self.root)

        self.tree.SetItemPyData(self.root,self.model.hdf5.root)
        for leaf in self.model.hdf5.root._v_leaves.keys():
            item = self.tree.AppendItem(self.root,leaf)
            self.tree.SetItemPyData(item,self.model.hdf5.root._v_leaves[leaf])
        for subGroup in self.model.hdf5.root._v_groups:
            self.UpdateTree(self.model.hdf5.root._v_groups[subGroup],self.root)
        for item in self.treeItems:
            # self.tree.Expand(item)
            if self.tree.GetItemPyData(item) == self.model.GetCurrentGroup():
                self.tree.SelectItem(item)
        # sort tree
        self.tree.SortChildren(self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeActivated, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnShowPopup, self.tree)

    def TreeItemsDefaultColor(self, parent=None):
        if parent is None:
            parent = self.root
        item, cookie = self.tree.GetFirstChild(parent)
        while item:
            self.tree.SetItemTextColour(item, 'black')
            self.TreeItemsDefaultColor(item)
            item, cookie = self.tree.GetNextChild(parent, cookie)


    def UpdateTree(self, newH5Group, curTreeGroup, data = None):
        self.curData = data
        newTreeGroup = self.tree.AppendItem(curTreeGroup, newH5Group._v_name)
        self.treeItems.append(newTreeGroup)
        self.tree.SetItemPyData(newTreeGroup,newH5Group)
#        if self.curData is not None and 'data' not in newH5Group._v_leaves.keys():
#            item = self.tree.AppendItem(newTreeGroup, 'data')
#            self.tree.SetItemPyData(item,self.curData)
        for leaf in newH5Group._v_leaves.keys():
            if leaf is 'data':
                self.curData = newH5Group._v_leaves[leaf]
            item = self.tree.AppendItem(newTreeGroup,leaf)
            self.tree.SetItemPyData(item,newH5Group._v_leaves[leaf])
        for subGroup in newH5Group._v_groups.keys():
            self.UpdateTree(newH5Group._v_groups[subGroup],newTreeGroup, self.curData)

    def OnTreeActivated(self,event):
        self.log.Clear()
        obj = self.tree.GetItemPyData(event.GetItem())
        self.log.WriteText( self.model.TextInfo(obj) + "\n")
        self.model.SelectGroup(obj)
        self.TreeItemsDefaultColor()
        self.tree.SetItemTextColour(event.GetItem(),'red')
        if self.model.IsZ():
            if self.zPopMenuItem is None:
                self.zPopMenuItem = self.popup.Append(-1, "Edit Z Labels")
                self.Bind(wx.EVT_MENU, self.OnZEdit, self.zPopMenuItem)

        else:
            if self.zPopMenuItem is not None:
                self.popup.Remove(self.zPopMenuItem.GetId() )
                self.Unbind(wx.EVT_MENU, self.zPopMenuItem)
                self.zPopMenuItem.Destroy()
                self.zPopMenuItem = None

    def OnTreeRightClick(self,event):
        if self.tree.GetItemPyData(event.GetItem())._c_classId == "GROUP":
            pass
        elif self.tree.GetItemPyData(event.GetItem())._c_classId == "ARRAY":
            pass

    def OnTreeEdit(self,event):
        if event.GetItem() == self.root:
            event.Veto()
        else:
            item = self.tree.GetItemPyData(event.GetItem())
            label = event.GetLabel()
            if label:
                item._f_rename(label)

    def OnZEdit(self, event):
        self.obo = OboTreeFrame(self.model, self)
        self.obo.Show()

    def CreateEdit(self):
        try:
            return self.edit
        except:
            menu = wx.Menu()
            self.popupItems = {}
            self.pasteItem = None
            for str in ['Edit','Cut','Copy','Paste', 'New Group', 'Rename', 'Delete', 'Export', 'Annotate', 'Batch', 'Remote Process']:
                self.popupItems[str] = menu.Append(-1, str)
                self.Bind(wx.EVT_MENU, self.OnPopupSelected, self.popupItems[str])

            self.popupItems['Paste'].Enable(False)
            return menu

    def OnDisplayItem(self, event):
        if self.tree.GetItemPyData(event.GetItem())._c_classId != 'GROUP':
            table = EditFrame(self.tree.GetItemPyData(self.tree.GetSelection()))
            table.Show()

    def CreatePopup(self):
        menu = self.CreateEdit()
        self.io = Io(self.model, self)
        self.io.LoadPlugins()

        self.openMenu = menu.AppendMenu(-1,
                                         "Import...",
                                         self.io.BuildOpenMenu())

        return menu

    def OnShowPopup(self, event):
        if self.tree.GetItemPyData(event.GetItem())._c_classId == "GROUP":
            self.popupItems['Edit'].Enable(False)
            self.popupItems['Annotate'].Enable(True)
        else:
            self.popupItems['Edit'].Enable(True)
            self.popupItems['Annotate'].Enable(False)
        if 'batch' in self.tree.GetItemPyData(event.GetItem())._v_attrs:
            self.popupItems['Batch'].Enable(True)
        else:
            self.popupItems['Batch'].Enable(False)
        self.tree.PopupMenu(self.popup)

    def OnPopupSelected(self, event):
        item = self.popup.FindItemById(event.GetId())
        self.OnMenuSelect(item)

    def OnMenuSelect(self, item):
        text = item.GetText()
        if text == 'Edit':
            table = EditFrame(self.tree.GetItemPyData(self.tree.GetSelection()))
            table.Show()
        elif text == 'New Group':
            self.OnNewGroup()
        elif text == 'Copy':
            self.OnCopy()
        elif text == 'Cut':
            self.OnCut()
        elif text == 'Paste':
            self.OnPaste()
        elif text == 'Rename':
            self.OnRename()
        elif text == 'Delete':
            self.OnDelete()
        elif text == 'Export':
            self.OnExport()
        elif text == 'Annotate':
            self.OnAnnotate()
        elif text == 'Batch':
            self.OnBatch()
        elif text == 'Remote Process':
            self.OnSubmitJob(None)
        else:
            wx.MessageBox(text)

    def OnBatch(self):

        source = self.model.GetCurrentData()
        choices = self.model.GetDataGroups()
        #print source._v_pathname
        try:
            choices.remove(self.GetCurrentGroup()._v_pathname)
        except:
            pass
        dialog = wx.MultiChoiceDialog(None, "Chose groups to apply " +source.getAttr('batch')[0] + " to",
                                       "choices", choices)
        batchOp = source.getAttr('batch')
        transforms = { 'scale' : self.model.ScaleTransform,
                      'normal scale' : self.model.NormalScaleTransform,
                      'clip' : self.model.ClipTransform,
                      'linear' : self.model.LinearTransform,
                      'quadradic' : self.model.QuadraticTransform,
                      'log' : self.model.LogTransform,
                      'logn': self.model.LognTransform,
                      'biexponential':self.model.BiexponentialTransform,
                      'logicle': self.model.LogicleTransform,
                      'heyerlog': self.model.HyperlogTransform,
                      'arcsin': self.model.ArcsinhTransform }


        if dialog.ShowModal() == wx.ID_OK:
            print [choices[i] for i in dialog.GetSelections()]
            if batchOp[0] == 'gate':
                self.OnBatchGate(source, [choices[i] for i in dialog.GetSelections()])
            elif batchOp[0] == 'qgate':
                self.OnBatchGate(source, [choices[i] for i in dialog.GetSelections()], quad=True)
            elif batchOp[0] in transforms.keys():
                for i in dialog.GetSelections():
                    self.model.SelectGroupByPath(choices[i])
                    transforms[batchOp[0]](batchOp[1], batchOp[2])
            else:
                print source.getAttr('batch')[0]

    def OnBatchGate(self, source, dest, quad=False):
        x,y = source.getAttr('batch')[1]
        if quad:
            for group in dest:
                self.model.SelectGroupByPath(group)
                if x and y in self.model.GetCurrentData().getAttr('fields'):
                    xline, yline = source.getAttr('batch')[2]
                    window = self.Visuals['2D Density'](self, show=False)
                    window.AttachModel(self.model)
                    window.radioX.SetStringSelection(x)
                    window.radioY.SetStringSelection(y)
                    window.OnControlSwitch(-1)
                    window.OnAddQuadGate(-1)
                    window.widget.vline._x = [xline,xline]
                    window.widget.hline._y = [yline,yline]
                    window.Gate(-1)
                    window.Destroy()
                else:
                    dialog = wx.MessageDialog(self, "Unable to find matching fields for " + group, style=wx.OK)
                    if dialog.ShowModal() == wx.ID_OK:
                        pass
        else:
            for group in dest:
                self.model.SelectGroupByPath(group)
                if x and y in self.model.GetCurrentData().getAttr('fields'):
                    window = self.Visuals['2D Density'](self, show=False)
                    window.AttachModel(self.model)
                    window.radioX.SetStringSelection(x)
                    window.radioY.SetStringSelection(y)
                    window.OnControlSwitch(-1)
                    window.OnAddPolyGate(-1)
                    window.widget.p.poly.verts = list(source.getAttr('batch')[2])
                    window.widget.p.poly_changed(window.widget.p.poly)
                    window.Gate(-1)
                    window.Destroy()
                else:
                    dialog = wx.MessageDialog(self, "Unable to find matching fields for " + group, style=wx.OK)
                    if dialog.ShowModal() == wx.ID_OK:
                        pass
    def OnAnnotate(self):
        selection = self.tree.GetSelection()
        item = self.tree.GetItemPyData(selection)
        txt = self.tree.GetItemText(selection)
        current = self.model.GetCurrentAnnotation()
        if current is not None:
            notes = map(lambda x, y: (x,y), current[:,0],current[:,1])
        else:
            notes = None
        annotate = annotateFrame(item, self.model, txt, notes)
        annotate.Show()

    def OnRename(self):
        selection = self.tree.GetSelection()
        if selection != self.root:
            self.tree.EditLabel(selection)
            item = self.tree.GetItemPyData(selection)
            label = self.tree.GetItemText(selection)
            if label:
                item._f_rename(label)

    def OnDelete(self):
        self.model.deleteNode(self.tree.GetItemPyData(self.tree.GetSelection()))
        self.model.update()

    def OnCut(self):
        self.OnCopy(cut=True)

    def OnCopy(self, cut=False):
        self._cut = cut
        self._source = self.tree.GetItemPyData(self.tree.GetSelection())
        self.popupItems['Paste'].Enable(True)

    def OnPaste(self):
        self.model.copyNode(self._source, self.model.GetCurrentGroup())
        if self._cut:
            self.model.deleteNode(self._source)
            self._cut = False
            self.popupItems['Paste'].Enable(False)
        self.model.update()

    def OnNewGroup(self):
        name = wx.GetTextFromUser('Name for new group', caption='Create New Group', default_value='',
                                  parent = None)
        if name is not '':
            self.model.NewGroup(name)
            self.model.update()

    def OnExport(self):
        # window = DBDialog(self.model)
        # window.Show()
        """Export data associated with current group."""
        if self.model.ready:
            x = self.model.GetCurrentData()[:]
            cs = self.model.GetCurrentData().getAttr('fields')
            print cs
        else:
            wx.MessageBox("No data found")
            return

        dlg = ChoiceDialog(cs)
        if dlg.ShowModal() == wx.ID_OK:
            indices = dlg.GetSelections()
        dlg.Destroy()

        wildcard = "Tab-delimited (*.out)|*.out"
        dialog = wx.FileDialog(parent=self,
                               wildcard=wildcard,
                               message="Export Data",
                               defaultDir=self.exportDir,
                               style=wx.SAVE|wx.OVERWRITE_PROMPT)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()

            self.exportDir = os.path.split(path)[0]

            if path.split('.')[-1] in ['out']:
                ext = ''
            else:
                ext = '.out'

            datafile = path + ext
            savetxt(datafile, x[:,indices], delimiter='\t')
            savetxt(datafile.replace('out', 'txt'),
                    array(cs)[indices], fmt='%s')

#             fo = open(path + ext, 'w')
#             fo.write('\n'.join(['\t'.join(map(str, item))
#                                 for item in x[:,indices]]))
#             fo.close()

#             # store associated headers
#             fo = open(path + '.txt', 'w')
#             fo.write('\n'.join([header for header in array(cs)[indices]]))
#             fo.close()

        dialog.Destroy()

def parsejob(jobfile):
    results = []
    file = open(jobfile, 'r')
    for line in file:
        line = line.replace('\n','')
        tmp = line.split('\t')
        type = strip_quotes(tmp[0])
        args = strip_quotes(tmp[1])
        more = [strip_quotes(x) for x in tmp[2:]]
        results.append((type, args, more))
    file.close()
    print results
    return results

def strip_quotes(str):
    # gotta be a more sane way to do this...
    return str.replace("'",'').replace('"','')

if __name__ == '__main__':
    print parsejob('/home/jolly/foo.txt')
