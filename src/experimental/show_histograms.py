"""Simple GUI interface to CFSE fitting functions"""

import wx
import numpy
import sys
sys.path.extend(['..', '../plugins/visual/HistogramFrame'])
from dialogs import ParameterDialog, ChoiceDialog
from Main import HistogramPanel

class Model(object):
    """Model to store and manipulate data."""
    def __init__(self):
        self.sample = None
        self.control = None
        self.sample_fit = None
        self.control_fit = None

    def fit_data(self, inputs):
        """Fit normals to data."""
        print "Fitting data to inputs: ", inputs

    def fit_sample(self, inputs):
        """Fit normals to sample data."""
        self.data = self.sample
        self.fit_data(inputs)

    def fit_control(self, inputs):
        """Fit normals to control data."""
        self.data = self.control
        self.fit_data(inputs)

class CFSEApp(wx.App):
    """Main application for fitting normals to CFSE data."""
    def __init__(self, redirect=False):
        wx.App.__init__(self, redirect)
        self.frame = MainFrame("CFSE fitting application")
        self.frame.Show(True)

    def OnInit(self):
        return True

class MainFrame(wx.Frame):
    """Main frame for CFSE application."""
    def __init__(self, title="", pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.Frame.__init__(self, None, -1, title, pos, size)

        fileMenu = wx.Menu()
        load_sample = fileMenu.Append(-1, "Load sample data")
        load_control = fileMenu.Append(-1, "Load control data")

        analysisMenu = wx.Menu()
        self.fit_sample = analysisMenu.Append(-1, "Fit sample data")
        self.fit_control = analysisMenu.Append(-1, "Fit control data")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.histogram_sample = HistogramPanel(None, 1, self)
        self.histogram_sample.name = 'Sample data'
        self.histogram_control = HistogramPanel(None, 1, self)
        self.histogram_control.name = 'Control data'
        self.SetSizer(self.sizer)
        self.Fit()

        self.menuBar = wx.MenuBar()
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(analysisMenu, "&Analysis")
        self.SetMenuBar(self.menuBar)
        self.CreateStatusBar()
        self.SetStatusText("Ready")
        self.Bind(wx.EVT_MENU, self.OnLoadSample, load_sample)
        self.Bind(wx.EVT_MENU, self.OnLoadControl, load_control)
        self.Bind(wx.EVT_MENU, self.OnFitSample, self.fit_sample)
        self.Bind(wx.EVT_MENU, self.OnFitControl, self.fit_control)

        # disable menu events until pre-conditions met
        self.menuBar.Enable(self.fit_control.GetId(), False)
        self.menuBar.Enable(self.fit_sample.GetId(), False)

        self.model = Model()

    def read_data(self, file):
        """Simple data reader.

        Expects floating point numbers in plain text separated by white space.
        """
        try:
            return numpy.array(map(float, open(file).read().strip().split()))
        except Exception, e:
            print e
            return None

    def OnLoadData(self, event):
        """Generic data loader."""
        dlg = wx.FileDialog(self, 
                            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                            defaultDir='.',
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
        else:
            file = None
        dlg.Destroy()
        return file

    def OnLoadSample(self, event):
        """Load a sample file for fitting."""
        file = self.OnLoadData(event)
        self.model.sample = self.read_data(file)
        if self.model.sample is not None:
            self.menuBar.Enable(self.fit_sample.GetId(), True)
            self.SetStatusText("Sample data loaded")
            self.histogram_sample.x = self.model.sample
            self.histogram_sample.draw()
            self.sizer.Add(self.histogram_sample)
            self.Fit()

    def OnLoadControl(self, event):
        """Load a control file with well-defined peaks."""
        file = self.OnLoadData(event)
        self.model.control = self.read_data(file)
        if self.model.control is not None:
            self.menuBar.Enable(self.fit_control.GetId(), True)
            self.SetStatusText("Control data loaded")
            self.histogram_control.x = self.model.control
            self.histogram_control.draw()
            self.sizer.Add(self.histogram_control)


    def OnFitData(self, event):
        """Generic data fitting."""
        inputs = {}
        dlg = ParameterDialog([('mix_interval', 'FloatValidator', str(50.0)),
                               ('max_intervall', 'FloatValidator', str(100.0))],
                               inputs,
                               'Some information to help the fitting')
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
        return inputs

    def OnFitSample(self, event):
        """Fit the sample data."""
        inputs = self.OnFitData(event)
        self.model.fit_sample(inputs)
        if self.model.sample_fit is not None:
            self.SetStatusText("Sample data fitted")

    def OnFitControl(self, event):
        """Fit the control data."""
        inputs = self.OnFitData(event)
        self.model.fit_control(inputs)
        if self.model.control_fit is not None:
            self.SetStatusText("Control data fitted")

if __name__ == '__main__':
    app = CFSEApp()
    app.MainLoop()
