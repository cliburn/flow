"""Simple GUI interface to CFSE fitting functions"""

import wx
import numpy
import sys
sys.path.extend(['..', '../plugins/visual/HistogramFrame',
                 '/Volumes/HD2/hg/cfse_old/python'])
from dialogs import ParameterDialog, ChoiceDialog
from Main import HistogramPanel
from cfse_optimize import *

class Model(object):
    """Model to store and manipulate data."""
    def __init__(self):
        self.sample = None
        self.control = None
        self.sample_fit = None
        self.control_fit = None

    def fit_data(self, inputs, peaks=None, max_shift=10.0, scale_factor=50.0):
        """Fit normals to data."""
        if peaks is None:
            print "Fitting data to inputs: ", inputs
            min_interval = inputs['min_interval']
            max_interval = inputs['max_interval']
            span = 30
            overlap = 29
            adict = build_freq_dict(self.data)
            f1 = build_func_from_dict(adict)
            xmin, xmax = get_bounds(adict, span=0.995)

            resolution = 1
            peaks = find_fuzzy_peaks(xmin, xmax, min_interval, max_interval, resolution, span, overlap, f1)
        
        data = numpy.reshape(self.data, (len(self.data), 1))
        peaks = numpy.array(peaks)
        peaks = numpy.reshape(peaks, (1, len(peaks)))
        mu, sd, counts = cfse_em(data, peaks, scale_factor, max_shift)

        print mu, sd, counts
        return data, mu, sd, counts
        

    def fit_sample(self, inputs):
        """Fit normals to sample data."""
        self.data = self.sample
        return self.fit_data(inputs, peaks=self.ctrl_mu, max_shift=0.0,
                             scale_factor=50.0)

    def fit_control(self, inputs):
        """Fit normals to control data."""
        self.data = self.control
        x, mu, sd, counts = self.fit_data(inputs)
        self.ctrl_mu = mu
        return x, mu, sd, counts

class CFSEApp(wx.App):
    """Main application for fitting normals to CFSE data."""
    def __init__(self, redirect=False):
        wx.App.__init__(self, redirect)
        self.frame = MainFrame("CFSE fitting application")
        # self.frame.Show(True)

    def OnInit(self):
        return True

class HistogramFrame(wx.Frame):
    """Frame to display control and sample Histograms."""
    def __init__(self, title="", name="",  pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.Frame.__init__(self, None, -1, title, pos, size)

        self.widget = HistogramPanel(None, 1, self, -1)
        self.widget.name = name
        self.widget.draw()
        self.Show()

    def update(self, x):
        self.widget.x = x
        self.widget.draw()

    def plot_fit(self, x, mu, sd, counts):
        self.widget.plot_fit(x, mu, sd, counts)

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

        self.histogram_control = HistogramFrame("Control histogram", "Control", (0, 22), (600,400))
        self.histogram_sample = HistogramFrame("Sample histogram", "Sample", (600, 22), (600,400))

        self.model = Model()
        self.maxpts = 10000

    def read_data(self, file):
        """Simple data reader.

        Expects floating point numbers in plain text separated by white space.
        """
        try:
            return 100*numpy.array(map(float, open(file).read().strip().split()))
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
        self.model.sample = self.read_data(file)[:self.maxpts]
        if self.model.sample is not None:
            self.menuBar.Enable(self.fit_sample.GetId(), True)
            self.SetStatusText("Sample data loaded")
            self.histogram_sample.update(self.model.sample)

    def OnLoadControl(self, event):
        """Load a control file with well-defined peaks."""
        file = self.OnLoadData(event)
        self.model.control = self.read_data(file)[:self.maxpts]
        if self.model.control is not None:
            self.menuBar.Enable(self.fit_control.GetId(), True)
            self.SetStatusText("Control data loaded")
            self.histogram_control.update(self.model.control)

    def OnFitData(self, event):
        """Generic data fitting."""
        inputs = {}
        dlg = ParameterDialog([('min_interval', 'FloatValidator', str(60.0)),
                               ('max_interval', 'FloatValidator', str(110.0))],
                               inputs,
                               'Some information to help the fitting')
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
        return inputs

    def OnFitSample(self, event):
        """Fit the sample data."""
        # inputs = self.OnFitData(event)
        x, mu, sd, counts = self.model.fit_sample(inputs=None)
        self.histogram_sample.plot_fit(x, mu, sd, counts)

        if self.model.sample_fit is not None:
            self.SetStatusText("Sample data fitted")

    def OnFitControl(self, event):
        """Fit the control data."""
        inputs = self.OnFitData(event)
        
        x, mu, sd, counts = self.model.fit_control(inputs)
        self.histogram_control.plot_fit(x, mu, sd, counts)

        if self.model.control_fit is not None:
            self.SetStatusText("Control data fitted")

if __name__ == '__main__':
    app = CFSEApp()
    app.MainLoop()
