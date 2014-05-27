import wx
import wx.html
import webbrowser

class FlowAbout(wx.Dialog): 
    text = ''' 
<html> 
<body bgcolor="#eeeeee"> 
<center><table bgcolor="#ff9900" width="100%" cellspacing="0" 
cellpadding="0" border="1"> 
<tr> 
    <td align="center"><h1>Flow!</h1></td> 
</tr> 
</table> 
</center> 
<p><b>Flow</b> is a program that integrates visualization, informatics and statistics to provide a better platform for analyzing multi-color flow cytomety data sets. The latest version can always be downloaded from the program homepage at <a href=http://galen.dulci.duhs.duke.edu/flow/wiki/>http://galen.dulci.duhs.duke.edu/flow</a>
</p> 
<p><b>Flow</b> was created by Cliburn Chan, Jacob Frelinger and Thomas Kepler at the Duke University Center for Computational Immunology.
</body> 
</html> 
''' 

    def __init__(self, parent): 
        wx.Dialog.__init__(self, parent, -1, 'About Flow', 
                          size=(440, 400) ) 
        html = NativeBrowserHtmlWindow(self) 
        html.SetPage(self.text) 
        button = wx.Button(self, wx.ID_OK) 
        sizer = wx.BoxSizer(wx.VERTICAL) 
        sizer.Add(html, 1, wx.EXPAND|wx.ALL, 5) 
        sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5) 
        self.SetSizer(sizer) 
        self.Layout() 

class NativeBrowserHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, -1)

    def OnLinkClicked(self, link):
        try:
            webbrowser.open(link.GetHref())
        except:
            wx.MessageBox("Cannot open %s" % link.GetHref(), wx.ID_OK)
