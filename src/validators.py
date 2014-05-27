import wx

class BasicValidator(wx.PyValidator):
    def __init__(self, data, key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key
        
    def Clone(self):
        """
        Note all validators musse implement Clone()
        """
        return BasicValidator(self.data, self.key)
    def Validate(self,win):
        return True
    def TransferToWindow(self):
        pass
    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = textCtrl.GetValue()
        
class IntValidator(wx.PyValidator):
    def __init__(self, data, key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key
    def Clone(self):
        """
        Note all validators musse implement Clone()
        """
        return IntValidator(self.data, self.key)

    def Validate(self,win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        
        try:
            int(text)
        except ValueError:
            textCtrl.SetBackgroundColour('pink')
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        
        textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        textCtrl.Refresh()
        return True

    def TransferToWindow(self):
        pass
    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = int(textCtrl.GetValue())
        
class FloatValidator(wx.PyValidator):
    def __init__(self,data,key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key

    def Clone(self):
        """
        Note all validators musse implement Clone()
        """
        return FloatValidator(self.data, self.key)
        
    def Validate(self,win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        
        try:
            float(text)
        except ValueError:
            #print text
            textCtrl.SetBackgroundColour('pink')
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        
        textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        textCtrl.Refresh()
        return True
    def TransferToWindow(self):
        pass
    def TransferFromWindow(self):
        textCtrl = self.GetWindow()
        self.data[self.key] = float(textCtrl.GetValue())