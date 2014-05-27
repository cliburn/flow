from plugin import Statistics
from validators import IntValidator, FloatValidator

import wx
import sys
import numpy
import operator
import threading
sys.path.append('plugins/statistics/Kde')
try:
    print "Importing ..."
    import flow
    print "flow"
except:
    pass

class KDE(Statistics):
    """class to do KDE"""
    name="KDE"

    def Main(self, model):
        """main"""
        frame = KDEFrame(model)
        
class KDEFrame(wx.Frame):
    def __init__(self, model):
        wx.Frame.__init__(self,None,-1, "KDE progress", size=(200,100))
        self.panel = wx.Panel(self)
        data = model.GetCurrentData()[:]
        self.group = model.GetCurrentGroup()
        self.model = model
        inputs = {}
        self.log = wx.TextCtrl(self.panel, -1, "",
                                       style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY, size=(200,100))
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.panel, 1, wx.ALL|wx.EXPAND)
        self.log.FitInside()
        self.SetSizer(box)
        self.dialog = KDEDialog(inputs)
        rtrn = self.dialog.ShowModal()
        print inputs
        self.dialog.Destroy()
        
        if rtrn == wx.ID_OK:
            self.Show()
            thread = KDEThread(self, data, inputs)
            thread.start()

    def Log(self, msg):
        self.log.AppendText(str(msg) )
        self.log.AppendText("\n")
                
    def ThreadFinish(self, returns):
        z, mm = returns
        self.model.NewGroup('KDE')
        #model.hdf5.copyNode(model.current_group._v_parent, newparent=model.current_group,name='data',newname='data')
        self.model.NewArray('modes', mm)
        self.model.NewArray( 'z', z)
        self.model.update()
        
    def NoMM(self):
        dialog = wx.MessageDialog(None, "No MMs found", "No MMs Found", wx.OK | wx.ICON_INFORMATION )
        dialog.ShowModal()
        
        
class KDEThread(threading.Thread):
    """
    thread runner to actually do kde computation
    """
    def __init__(self, window, data, inputs):
        threading.Thread.__init__(self)
        self.window = window
        self.data = data
        self.n, self.dim = numpy.shape(data)
        self.k = self.n
        self.inputs = inputs
        self.h = inputs['h']
        self.TimeToQuit = threading.Event()
        self.TimeToQuit.clear()
    
    def stop(self):
        self.TimeToQuit.set()
    
    def run(self):
        
        wx.CallAfter(self.window.Log, "Creating Epanechnikov analyzer using factory method")
        ap = flow.create_analyzer("Epanechnikov", self.data, self.dim, self.n, self.k, self.h, 0.0)

        wx.CallAfter(self.window.Log, "Test find seeds")
        # min_sep = ap.calc_h()
        # print min_sep
        min_sep = 0.1
        # seeds = ap.find_seeds(min_sep, 10, 100)
        seeds = ap.find_seeds_simple(self.inputs['seeds'])
        wx.CallAfter(self.window.Log, "num seeds:" + str(len(seeds)))
    
        wx.CallAfter(self.window.Log, "Test find modes")
        modes = ap.find_modes(seeds, 1e-4)
        wx.CallAfter(self.window.Log, "num modes:" + str(len(modes)))
        # for mode in modes:
            # print mode, modes[mode]
    
        wx.CallAfter(self.window.Log, "Test merge modes")
        min_merge_sep = 1.0
        mmodes = ap.merge_modes(modes, min_merge_sep)
        
        wx.CallAfter(self.window.Log, "Test dip")
        dip_ratio = self.inputs['dip']
        mmodes = ap.check_modes(mmodes, dip_ratio)
        wx.CallAfter(self.window.Log, "num dip modes:" + str(len(mmodes)))
        wx.CallAfter(self.window.Log, mmodes)
        # for mmode in mmodes:
            # print mmode, mmodes[mmode]
            #         print ">>>", data_unscaled[mmodes[mmode][0]]
    
        wx.CallAfter(self.window.Log, "Test label seeds")
        # seed_labels = flow.label_seeds(mmodes)
        # for seed_label in seed_labels:
            # print seed_label, seed_labels[seed_label]
    
        wx.CallAfter(self.window.Log, "Test label points")
        # nbrs = 1+int(numpy.floor(len(mmodes)/5.0))
        nbrs = 1
        clusters = flow.label_points("Epanechnikov", self.data, mmodes, nbrs)
        #counts = {}
        #for k in clusters.values():
        #    counts[k] = counts.get(k, 0) + 1
        #print counts
        z = []
        for i in clusters.keys():
            z.append(clusters[i])

        # save modes in order of number of captured seeds
        items = [(k, len(v)) for k, v in mmodes.items() if len(v) > 1]
        items.sort(key = operator.itemgetter(1), reverse=True)
        wx.CallAfter(self.window.Log, "Modes found that pass dip and pop tests")
        wx.CallAfter(self.window.Log, items)
        mm = numpy.array([item[0] for item in items])
        if mm.size == 0:
            wx.CallAfter(self.window.NoMM)
        else:
            wx.CallAfter(self.window.ThreadFinish, (z,mm))
        
        
class KDEDialog(wx.Dialog):
    def __init__(self,data):
        wx.Dialog.__init__(self,None,-1, "KDE parameters")
        h_text = wx.StaticText(self, -1, "h:")
        # alpha_text = wx.StaticText(self,-1, "Alpha:")
        seeds_text = wx.StaticText(self,-1, "Number of Seeds:")
        dip_text = wx.StaticText(self,-1, "Dip Ratio:")
        h_input = wx.TextCtrl(self, validator=FloatValidator(data,'h'))
        # alpha_input = wx.TextCtrl(self,validator=FloatValidator(data,'alpha'))
        seeds_input = wx.TextCtrl(self,validator=IntValidator(data,'seeds'))
        dip_input = wx.TextCtrl(self,validator=FloatValidator(data,'dip'))
        
        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        canel = wx.Button(self, wx.ID_CANCEL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        fgs = wx.FlexGridSizer(4,2,5,5)
        fgs.Add(h_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(h_input, 0, wx.EXPAND)
        # fgs.Add(alpha_text, 0 , wx.ALIGN_RIGHT)
        # fgs.Add(alpha_input, 0, wx.EXPAND)
        fgs.Add(seeds_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(seeds_input, 0, wx.EXPAND)
        fgs.Add(dip_text, 0 , wx.ALIGN_RIGHT)
        fgs.Add(dip_input, 0, wx.EXPAND)
        fgs.AddGrowableCol(1)
                
        sizer.Add(fgs,0,wx.EXPAND|wx.ALL,5)
        
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(okay)
        btns.AddButton(canel)
        btns.Realize()
        
        sizer.Add(btns,0,wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
