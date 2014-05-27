from plugin import Statistics
from validators import IntValidator, FloatValidator

import wx
import sys
import numpy
import operator
import threading
# sys.path.append('c++/bayes/')
import bayes

class Bayes(Statistics):
    name="Bayes"

    def Main(self, model):
        frame = BayesFrame(model)

class BayesFrame(wx.Frame):
    def __init__(self, model):
        wx.Frame.__init__(self,None,-1, "MCMC progress", size=(200,100))
        self.panel = wx.Panel(self)
        self.data = model.GetCurrentData()[:]
        self.current_group = model.current_group
        self.model = model
        x = numpy.transpose(self.data)
        n, p = numpy.shape(self.data)
        self.inputs = {}
        self.log = wx.TextCtrl(self.panel, -1, "",
                                       style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY, size=(200,100))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.panel, 1, wx.ALL|wx.EXPAND)
        self.log.FitInside()
        self.SetSizer(box)
        dialog = BayesDialog(self.inputs)
        rtrn = dialog.ShowModal()
        print self.inputs
        dialog.Destroy()
        if rtrn == wx.ID_OK:
        
            print n
            print p
            
            self.k = self.inputs['k']
            nit = self.inputs['nit']
            nmc = self.inputs['nmc']

            b = bayesThread(self, x, n, p, self.k, nit, nmc)
            b.start()

    def Log(self, msg):
        self.log.AppendText(msg )
        self.log.AppendText("\n")
        
    def ThreadFinish(self, returns):
        save_pi, save_mu, pi, z, mu, Omega = map(numpy.array, returns)

        self.model.NewGroup('Bayes_%02d' % self.k)
        self.current_group = self.model.current_group
        self.model.hdf5.createArray(self.current_group, 'pi', save_pi)
        self.model.hdf5.createArray(self.current_group, 'z', list(z))
        self.model.hdf5.createArray(self.current_group, 'mu', save_mu)
        # self.model.hdf5.createArray(self.current_group, 'omega', Omega)

        self.model.hdf5.createArray(self.current_group, 'pi_end', list(pi))
        self.model.hdf5.createArray(self.current_group, 'mu_end', mu)
        self.model.hdf5.createArray(self.current_group, 'omega_end', Omega)

        self.model.SetGroupParams(self.inputs)
        self.model.update()
                

class bayesThread(threading.Thread):
    def __init__(self, window, x, n, p, k , nit, nmc):
        threading.Thread.__init__(self)
        self.window = window
        self.x = x
        self.n = n
        self.p = p
        self.k = k
        self.nit = nit
        self.nmc = nmc

    def run(self):
        wx.CallAfter(self.window.Log, "Creating Bayes class")
        self.b = bayes.Bayes()
        self.b.init(self.x, self.n, self.p, self.k)
        wx.CallAfter(self.window.Log, "Running mcmc sampler")
        self.b.mcmc(self.nit, self.nmc, ".out", 0)
        wx.CallAfter(self.window.ThreadFinish, 
                     (self.b.get_save_pi(), self.b.get_save_mu(), self.b.get_pi(), self.b.get_z(), self.b.get_mu(), self.b.get_Omega()))
        
                     
class BayesDialog(wx.Dialog):
    def __init__(self,data):
        wx.Dialog.__init__(self, None, -1, "MCMC parameters")
        k_text = wx.StaticText(self, -1, "Number of components:")
        nit_text = wx.StaticText(self, -1, "Number of burn iterations:")
        nmc_text = wx.StaticText(self, -1, "Number of mc iterations:")
        k_input = wx.TextCtrl(self, validator=IntValidator(data, 'k'))
        nit_input = wx.TextCtrl(self, validator=IntValidator(data, 'nit'))
        nmc_input = wx.TextCtrl(self, validator=IntValidator(data,'nmc'))

        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        canel = wx.Button(self, wx.ID_CANCEL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        fgs = wx.FlexGridSizer(4,2,5,5)
        fgs.Add(k_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(k_input, 0, wx.EXPAND)
        fgs.Add(nit_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(nit_input, 0, wx.EXPAND)
        fgs.Add(nmc_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(nmc_input, 0, wx.EXPAND)
        fgs.AddGrowableCol(1)
                
        sizer.Add(fgs,0,wx.EXPAND|wx.ALL,5)
        
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(okay)
        btns.AddButton(canel)
        btns.Realize()
        
        sizer.Add(btns,0,wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
