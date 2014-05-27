#!/usr/bin/env python

"""Main Aplication"""
import matplotlib
matplotlib.use('WXAgg')

import wx
import sys
import os
import glob
import os_utils

# added a comment
# import plugin directories
sys.path.append('plugins/visual'.replace("/", os.path.sep))
sys.path.append('plugins/io'.replace("/", os.path.sep))
sys.path.append('plugins/statistics'.replace("/", os.path.sep))
sys.path.append('plugins/projections'.replace("/", os.path.sep))
from plugin import loadFrames, loadstatistics, loadprojections
from MainFrame import MainFrame
from Model import FlowModel
from my_io import Io
from dialogs import SaveDialog
from compensation import CompensationFrame
from EditTable import SpillFrame
import about


class MainApp(wx.App): #IGNORE:R0902
    """main app class, used to start the whole program """
    framelist = []
    def OnInit(self):
        """OnInit method used by wxwindows.  initiates all base
        classes and methods
        """
        self.model = FlowModel()
        self.model.addListener(self.OnModelUpdate)

        self.controlFrame = MainFrame(pos=(50, 50))
        self.controlFrame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.controlFrame.Show()
        self.model.addListener(self.controlFrame.ModelUpdate)
        self.controlFrame.AttachModel(self.model)

        self.io = Io(self.model, self.controlFrame)
        self.io.LoadPlugins()

        self.fileMenu = wx.Menu()
        self.io.BuildOpenMenu(self.fileMenu)
        self.fileMenu.AppendSeparator()
        importFCSDir = self.fileMenu.Append(-1, "Load all FCS files in directory")
        importCSVDir = self.fileMenu.Append(-1, "Load all delimited files in directory")
        self.controlFrame.Bind(wx.EVT_MENU, self.OnImportFCSDir, importFCSDir)
        self.controlFrame.Bind(wx.EVT_MENU, self.OnImportCSVDir, importCSVDir)
        self.fileMenu.AppendSeparator()
        save = self.fileMenu.Append(-1,'Save HDF5 file')
        self.controlFrame.Bind(wx.EVT_MENU, self.OnSave, save)
        menuquit = self.fileMenu.Append(-1,'Quit')
        self.controlFrame.Bind(wx.EVT_MENU, self.OnQuit, menuquit)

        self.compensateMenu = wx.Menu()
        compensate = self.compensateMenu.Append(-1, 'Apply compensation')
        #load_comp = self.compensateMenu.Append(-1, 'Load compensation matrix')
        #edit_comp = self.compensateMenu.Append(-1, 'Edit compensation matrix')
        self.controlFrame.Bind(wx.EVT_MENU, self.OnCompensate, compensate)
        #self.controlFrame.Bind(wx.EVT_MENU, self.OnLoadCompensate, load_comp)
        #self.controlFrame.Bind(wx.EVT_MENU, self.OnEditCompensate, edit_comp)

        self.graphicsMenu = wx.Menu()
        self.visuals = loadFrames("plugins/visual")
        self.controlFrame.Visuals = self.visuals
        for key in self.visuals:
            menuid = self.graphicsMenu.Append(-1, key)
            self.controlFrame.Bind(wx.EVT_MENU, self.OnAddWindow, menuid)
        self.graphicsMenu.AppendSeparator()

        self.statisticsMenu = wx.Menu()
        self.statistics = loadstatistics("plugins/statistics")
        for key in self.statistics.keys():
            menuid = self.statisticsMenu.Append(-1, key)
            self.controlFrame.Bind(wx.EVT_MENU, self.Onstatistics, menuid)

        self.projectionsMenu = wx.Menu()
        self.projections = loadprojections("plugins/projections")
        for key in self.projections.keys():
            menuid = self.projectionsMenu.Append(-1, key)
            self.controlFrame.Bind(wx.EVT_MENU, self.Onprojections, menuid)

        menuItems = [(self.fileMenu, 'File'),
                     (self.controlFrame.edit, 'Tree'),
                     (self.compensateMenu, 'Compensation'),
                     (self.controlFrame.filterMenu, 'Sub-Sample'),
                     (self.controlFrame.transformMenu, 'Transformation'),
                     (self.graphicsMenu, 'Graphics'),
                     (self.statisticsMenu, 'Statistics'),
                     (self.projectionsMenu, 'Projection'),
                     (self.controlFrame.ontologyMenu, 'Ontology'),
                     (self.controlFrame.remoteProcessMenu, 'Server')]
        for item in menuItems:
            self.controlFrame.GetMenuBar().Append(*item)

        # help menu
        self.helpMenu = wx.Menu()
        self.about = self.helpMenu.Append(wx.ID_ABOUT, "&About Flow")
        self.help = self.helpMenu.Append(-1, "Flow User Guide")
        self.developer = self.helpMenu.Append(-1, "Flow Developer Guide")
        # self.tutorial = self.helpMenu.Append(-1, "Flow Tutorial")
        self.helpMenu.AppendSeparator()
        self.homepage = self.helpMenu.Append(-1, "Flow homepage")
        self.bugs = self.helpMenu.Append(-1, "Report bugs")
        self.helpMenu.AppendSeparator()
        # self.update = self.helpMenu.Append(-1, "Check for updates")

        self.controlFrame.GetMenuBar().Append(self.helpMenu, "&Help")

        self.Bind(wx.EVT_MENU, self.OnAbout, self.about)
        self.Bind(wx.EVT_MENU, self.OnHelp, self.help)
        self.Bind(wx.EVT_MENU, self.OnDeveloper, self.developer)
        # self.Bind(wx.EVT_MENU, self.OnTutorial, self.tutorial)
        self.Bind(wx.EVT_MENU, self.OnHomepage, self.homepage)
        self.Bind(wx.EVT_MENU, self.OnBugs, self.bugs)
        # self.Bind(wx.EVT_MENU, self.OnUpdate, self.update)


        global Visual
        self.controlFrame.DoLayout()
        self.SetTopWindow(self.controlFrame)

        return True

    def OnCompensate(self, event): #IGNORE:W0613
        """Apply compensation matrix to data."""
        try:
            if hasattr(self.model.GetCurrentGroup(), 'spillover'):
                comp = CompensationFrame(self.model, matrix = self.model.GetCurrentGroup().spillover)
            else:
                comp = CompensationFrame(self.model)
            comp.Show()
        except ValueError:
            dlg = wx.MessageDialog(None, 'Check that ALL columns listed in spillover matrix are present in the data', 'Compensation Error', style=wx.OK)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()

    def OnLoadCompensate(self, event): #IGNORE:W0613
        """Loads a compensation file in ASCII format with following structure
        n,h_1,...,h_n,a_11,...,a_nn
        where n is the number of marker columns requiring compensation
        h_i is the header column name and
        a_ij are the entries in the spillover matrix
        just like 'SPILL' entry in FACSDiva 'SPILL'"""

        overwrite = True
        if self.model.getSpill():
            overwrite = False
            dlg = wx.MessageDialog(None,
                                   'Overwrite existing matrix?',
                                   'Load spillover matrix',
                                   style=wx.OK|wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                overwrite = True
            dlg.Destroy()
        if overwrite:
            filetype = "Text files (*.txt)|*.txt|CSV files (*.csv)|*.csv|All files (*.*)|*.*"
            dialog = wx.FileDialog(None,
                                   "Load compensation matrix",
                                   os.getcwd(),
                                   "" ,
                                   filetype,
                                   wx.OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                self.model.setSpill(open(path).read())
            dialog.Destroy()

    def OnEditCompensate(self, event): #IGNORE:W0613
        """Assumes that spillover matrix is stored within fields as SPILL."""
        if self.model.ready:
            spill, markers = self.model.getSpill()
            if spill:
                self.spillFrame = SpillFrame(spill, markers)
                self.spillFrame.Show()

    def OnImportFCSDir(self, event): #IGNORE:W0613
        """Import all fcs files in directory."""
        dlg = wx.DirDialog(None,
                           "Choose a directory with .fcs files:",
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            fs = glob.glob(dir + '/*.fcs')
            for f in fs:
                self.io.ReadFCS(f)
                self.model.SelectRoot()
        dlg.Destroy()

    def OnImportCSVDir(self, event): #IGNORE:W0613
        """Import all csv files in directory."""
        dlg = wx.DirDialog(None,
                           "Choose a directory with .out and .txt files:",
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            fs = glob.glob(dir + '/*.out')
            for f in fs:
                self.io.ReadCSV(f)
                self.model.SelectRoot()
        dlg.Destroy()

    def OnQuit(self, event): #IGNORE:W0613
        """Handle quit event"""
        try:
            if not self.model.isChanged:
                self.Exit()
            elif self.model.isOpen():
                dialog = SaveDialog()
                result = dialog.ShowModal()
                if result == wx.ID_YES:
                    self.SaveFile()
                    self.model.close()
                elif result == wx.ID_NO:
                    self.model.close()
                if result == wx.ID_YES or result == wx.ID_NO:
                    self.Exit()
                dialog.Destroy()
        except AttributeError:
            self.Exit()

    def OnSave(self, event): #IGNORE:W0613
        """Save the hdf5 file"""

        if self.model.isOpen:
            filetype = "HDF5 file (*.h5)|*.h5"
            dialog = wx.FileDialog(None,
                                   "Save Working Set",
                                   os.getcwd(),
                                   "" ,
                                   filetype,
                                   wx.SAVE|wx.OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                if path.split('.')[-1] == 'h5':
                    ext = ''
                else:
                    ext = '.h5'
                self.model.saveAs(path + ext)
                self.model.isChanged = False
        dialog.Destroy()


    def OnAddWindow(self, event):
        """add a new window frame"""
        newWindowType = self.controlFrame.GetMenuBar().FindItemById(event.GetId()).GetLabel() #IGNORE:C0301
        newWindow = self.visuals[newWindowType]()
        title = newWindow.GetTitle()
        title = title + " of " + str(self.model.current_array)
        newWindow.SetTitle(title)
        newWindow.AttachModel(self.model)
        newId = self.graphicsMenu.AppendCheckItem(-1, title)
        newId.Check(True)
        self.framelist.append((newWindow.GetId(), newId.GetId(), newWindow))
        self.controlFrame.Bind(wx.EVT_MENU, self.OnWindowSelect, newId)
        newWindow.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        newWindow.Plot()

    def OnWindowSelect(self, event):
        """handle selecting a window from the list of windows"""
        menuItem = self.controlFrame.GetMenuBar().FindItemById(event.GetId())

        for windowId, menuId, window in self.framelist: #IGNORE:W0612
            if menuItem.GetId() == menuId:
                if menuItem.IsChecked():
                    window.Show(True)
                    window.SetFocus()
                else:
                    window.Show(False)


    def OnCloseWindow(self, event):
        """on window close event destroy all windows"""
        if event.GetId() == self.controlFrame.GetId():
            self.OnQuit(event)

        else:
            for windowId, menuId, window in self.framelist:
                if event.GetId() == windowId:

                    window.Destroy()
                    self.graphicsMenu.Remove(menuId)
                    self.framelist.remove((windowId, menuId, window))

    def OnModelUpdate(self, model): #IGNORE:W0613
        """on model update do something"""
        #print "Model Update Called"

    def Onstatistics(self, event):
        """When Statistics menu events are called"""
        Name = self.controlFrame.GetMenuBar().FindItemById(event.GetId()).GetLabel() #IGNORE:C0301
        statistics = self.statistics[Name]()
        statistics.Main(self.model)

    def Onprojections(self, event):
        """When projections menu events are called"""
        Name = self.controlFrame.GetMenuBar().FindItemById(event.GetId()).GetLabel() #IGNORE:C0301
        projections = self.projections[Name]()
        projections.Main(self.model)

    def OnAbout(self, event):
        """About screen."""
        dlg = about.FlowAbout(self.controlFrame)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, event):
        os_utils.open(os.path.join("..", "docs", "userguide.pdf"))

    def OnDeveloper(self, event):
        os_utils.open(os.path.join("..", "docs", "developer_guide.pdf"))

    def OnTutorial(self, event):
        pass

    def OnHomepage(self, event):
        os_utils.open('http://galen.dulci.org/flow')

    def OnBugs(self, event):
        os_utils.open('http://galen.dulci.org/flow/newticket')

    def OnUpdate(self, event):
        pass

if __name__ == '__main__':
    App = MainApp(redirect=False) #IGNORE:C0103
    App.MainLoop()
