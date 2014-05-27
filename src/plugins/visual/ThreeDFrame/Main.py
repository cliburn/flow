"""Need type, Plot() and ModelUpdate()."""
import wx
import vtk
import numpy
import os

# from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
# use Enthought version copied from svn/enthought/src/lib/enthought/pyface/tvtk/wxVTKRenderWindowInteractor.py
# which fixes bug crashing wxVTKRenderWindowInteractor on GTK2
from wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
# from wxVTKRenderWindow import wxVTKRenderWindow as wxVTKRenderWindowInteractor
from VizFrame import VizFrame
from OboFrame import OboTreeFrame

class ThreeDFrameGating(VizFrame):
    """frame for viewing 3d data"""
    type = '3D Density'

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="3D Density"):
        VizFrame.__init__(self, parent, id, pos, title)
        self.widget = wxVTKRenderWindowInteractor(self,-1)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.widget.SetInteractorStyle(style)

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.1, 0.1, 0.7)
        self.widget.GetRenderWindow().AddRenderer(self.ren)


        self.data = None
        self.colors = None
        
        # layout the frame
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.leftPanel = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.box)
        self.box.Add(self.leftPanel,0, wx.EXPAND)
        self.box.Add(self.widget,1,wx.EXPAND)
        self.Layout()

        self.MenuBar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.GateMenu = wx.Menu()
        self.MenuBar.Append(self.FileMenu, "File")
        self.MenuBar.Append(self.GateMenu, "Gating")
        self.SetMenuBar(self.MenuBar)
        export = self.FileMenu.Append(-1, "Export graphics")
        self.Bind(wx.EVT_MENU, self.OnExport, export)
        self.colorGate = self.GateMenu.Append(-1, "Gate on visible colors only")
        self.Bind(wx.EVT_MENU, self.GateByColor, self.colorGate)
        self.colorGate.Enable(False)
        gate = self.GateMenu.Append(-1, "Capture gated events")
        self.boxAddMenuItem = self.GateMenu.Append(-1, "Add box gate")
        self.GateMenu.AppendSeparator()
        self.boxes = []
        self.Bind(wx.EVT_MENU, self.OnBox, self.boxAddMenuItem)
        
        self.Bind(wx.EVT_MENU, self.Gate, gate)

        self.selectActor = vtk.vtkLODActor()
        self.planes = {} #vtk.vtkPlanes()
        self.clipper = vtk.vtkClipPolyData()
        
        self.boxCount = 1
        self.boxIds = {}

        self.Show()
        self.SendSizeEvent()

    def OnBox(self, event):
        boxWidget = vtk.vtkBoxWidget()
        # change handle properties
        boxWidget.SetHandleSize(0.005) # default is 0.01
        boxWidget.SetInteractor(self.widget)
        boxWidget.SetPlaceFactor(1.25)
        boxWidget.SetInput(self.normals.GetOutput())
        boxWidget.PlaceWidget()
        boxCallback = self.BoxSelectPolygons()
        boxWidget.AddObserver("EndInteractionEvent", boxCallback)
        boxWidget.KeyPressActivationOff()
        plane = vtk.vtkPlanes()
        self.boxes.append(boxWidget)
        self.planes[boxWidget.GetAddressAsString('')] = plane
        self.region.AddFunction(plane)
        newId = self.GateMenu.AppendCheckItem(-1, "Box #" + str(self.boxCount))
        self.boxCount = self.boxCount + 1
        self.boxIds[newId.GetId()] = boxWidget.GetAddressAsString('')
        newId.Check(True)
        self.Bind(wx.EVT_MENU, self.OnBoxSelect, newId)
        boxWidget.On()

    def OnBoxSelect(self,event):
        id = event.GetId()
        menuItem = self.GetMenuBar().FindItemById(id)
        for box in self.boxes:
            if self.boxIds[id] == box.GetAddressAsString(''):
                print "mached a box"
                
                if menuItem.IsChecked(): # check just toggled so its bacwards..
                    self.region.AddFunction(self.planes[box.GetAddressAsString('')])
                    box.On()
                else:
                    self.region.RemoveFunction(self.planes[box.GetAddressAsString('')])
                    box.Off()
        self.SendSizeEvent()
                    
    def BoxSelectPolygons(self):
        def f(object, event):
            object.GetPlanes(self.planes[object.GetAddressAsString('')])
            self.selectActor.VisibilityOn()
        return f

    def ClearBoxes(self):
        for box in self.boxes:
            del box
        self.boxes = []
        self.planes = {}
        
    def OnExport(self, event):
        """Export to graphics filetype with extension ext."""
        renWin = self.widget.GetRenderWindow()
        wif = vtk.vtkWindowToImageFilter()
        wif.SetInput(renWin)

        wildcard = "PNG (*.png)|*.png|" \
            "Postscript (*.ps)|*.ps|" \
            "JPEG (*.jpg)|*.jpg"
            # "TIFF (*.tif)|*.tif"
        dialog = wx.FileDialog(None, "Export Graphics", os.getcwd(),
                               "", wildcard, wx.SAVE|wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            base, ext = os.path.splitext(path)
            if ext in ['.png', '.ps', '.jpg']:
                pass
            else:
                i = dialog.GetFilterIndex()
                ext = ['.png', '.ps', '.jpg'][i]
            # cases
            if ext == '.png':
                psw = vtk.vtkPNGWriter()
            elif ext == '.ps':
                psw = vtk.vtkPostScriptWriter()
            elif ext == '.jpg':
                psw = vtk.vtkJPEGWriter()
            psw.SetFileName(base + ext)
            psw.SetInput(wif.GetOutput())
            psw.Write()
        
    def RadioButtons(self,list):
        panel = wx.Panel(self,-1)
        self.radioX = wx.RadioBox(panel,-1,"X", wx.DefaultPosition, wx.DefaultSize, list,1,wx.RA_SPECIFY_COLS)
        self.radioY = wx.RadioBox(panel,-1,"Y", wx.DefaultPosition, wx.DefaultSize, list,1,wx.RA_SPECIFY_COLS)
        self.radioZ = wx.RadioBox(panel,-1,"Z", wx.DefaultPosition, wx.DefaultSize, list,1,wx.RA_SPECIFY_COLS)
        for i in [self.radioX, self.radioY, self.radioZ]:
            i.Bind(wx.EVT_RADIOBOX, self.OnControlSwitch)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.radioX,0)
        box.Add(self.radioY,0)
        box.Add(self.radioZ,0)
        panel.SetSizer(box)
        self.leftPanel.Insert(0,panel,0)

    def BuildLUT(self):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(self.maxcolor+1)
        lut.SetAlphaRange(1.0,1.0)
        lut.SetHueRange(0.0,.667)
        lut.SetSaturationRange(1.0,1.0)
        lut.SetTableRange(0, self.maxcolor)
        lut.SetRampToLinear()
        
        lut.Build()
        return lut

    def BuildColorPanel(self):
        panel = wx.ScrolledWindow(self,-1, style=wx.VSCROLL)
        c = [0, 0, 0]
        color_list = []
        for i in range(0,self.lut.GetNumberOfColors()):
            # GetColor changed between vtk4 and vtk5
            # below is the way blender gets around it
            try: # VTK5
                self.lut.GetColor(i, c)
                color_list.append(c[:])
            except: #VTK4
                color_list.append(self.lut.GetColor(i))
        color_names = self.model.GetZLabels(self.model.GetCurrentZ())
        # self.cbs = [wx.CheckBox(panel, -1, color_names[color_id]) for color_id, color in enumerate(color_list)]
          
        self.cbs = [wx.CheckBox(panel, -1, name) for name in color_names]
  
        self.popup = wx.Menu()
        zlabel = self.popup.Append(-1, "Edit label")
        self.popup.Bind(wx.EVT_MENU, self.OnZLabel, zlabel)
        
        for i, cb in enumerate(self.cbs):
            r, g, b = color_list[i]
            r = int(r*255)
            g = int(g*255)
            b = int(b*255)
            cb.SetValue(True)
            cb.SetBackgroundColour(wx.Colour(r,g,b))
            self.Bind(wx.EVT_CHECKBOX, self.DisableColors, cb)
            cb.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
            
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(self.cbs)
        panel.SetSizer(sizer)
        self.leftPanel.Insert(1,panel,1, wx.ALL | wx.EXPAND) 
        panel.SetScrollRate(5,5)

        return panel

    def OnShowPopup(self, event):
        self.PopupMenu(self.popup)
        
    def OnZLabel(self, event):
        obo = OboTreeFrame(self.model, self)
        obo.Bind(wx.EVT_WINDOW_DESTROY, self.OnOboClose)
        obo.Show()
        
    def OnOboClose(self, event):
        color_names = self.model.GetZLabels(self.model.GetCurrentZ())
        
        for i, cb in enumerate(self.cbs):
            cb.SetLabel(color_names[i])
            
    def BuildColors(self):
        # consider building a wxchecklistbox 
        if self.colors != None:
            self.maxcolor = int(max(self.colors))
        else:
            self.maxcolor = 0

        self.lut = self.BuildLUT()
        self.colorPanel = self.BuildColorPanel()

        if self.colors is None:
            self.colorPanel.Hide()
        self.Refresh()

    def TransformLabel(self, label, op_dict):
        labelTransform = vtk.vtkTransform()
        labelTransform.Identity()
        for op in op_dict:
            getattr(labelTransform, op)(op_dict[op])
        return labelTransform

    def TransformLabelFilter(self, label, labelTransform):
        labelTransformFilter = vtk.vtkTransformPolyDataFilter()
        labelTransformFilter.SetTransform(labelTransform)
        labelTransformFilter.SetInput(label.GetOutput())
        return labelTransformFilter
        
    def BuildLabelActor(self, text, op_dict):
        label = vtk.vtkVectorText()
        label.SetText(text)
        labelTransform = self.TransformLabel(label, op_dict)
        labelTransformFilter = self.TransformLabelFilter(label, labelTransform)
        labelMapper = vtk.vtkPolyDataMapper()
        labelMapper.SetInput(labelTransformFilter.GetOutput())
        actor = vtk.vtkFollower()
        actor.SetMapper(labelMapper)
        return actor

    def UpdateVTKWindow(self,x,y,z):
        self.widget.GetRenderWindow().RemoveRenderer(self.ren)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.1, 0.1, 0.7)
        self.widget.GetRenderWindow().AddRenderer(self.ren)

        scalars = vtk.vtkIntArray()
        
        self.pnt = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        self.pnt.SetNumberOfPoints(self.data.shape[0])
        cells.Allocate(self.data.shape[0],32)
        for i in xrange(0, self.data.shape[0]):
            if self.colors is not None:
                if self.cbs[self.colors[i]].IsChecked():     
                    self.pnt.InsertPoint(i,
                                    self.data[i,x],
                                    self.data[i,y],
                                    self.data[i,z])      
                    cells.InsertNextCell(1)
                    cells.InsertCellPoint(i)
            else:
                self.pnt.InsertPoint(i,
                                self.data[i,x],
                                self.data[i,y],
                                self.data[i,z])      
                cells.InsertNextCell(1)
                cells.InsertCellPoint(i)
        if self.colors is not None:
            for i in xrange(0, self.data.shape[0]):       
                scalars.InsertNextTuple1(self.colors[i])
        else:
            for i in xrange(0, self.data.shape[0]):       
                scalars.InsertNextTuple1(0)

        # create poly of the points
        self.poly = vtk.vtkPolyData()
        self.poly.SetPoints(self.pnt)
        self.poly.SetVerts(cells)
        self.poly.GetPointData().SetScalars(scalars)
        self.normals = vtk.vtkPolyDataNormals()
        self.normals.SetInput(self.poly)
        
        # add box widget for clipping
        # points inside the box are colored green
        apd = vtk.vtkAppendPolyData()
        apd.AddInput(self.poly)
        # create mapper pipline for the poly
        pntmapper = vtk.vtkPolyDataMapper()

        self.clipper.SetInput(apd.GetOutput())

        self.region = vtk.vtkImplicitBoolean()
        
        self.region.SetOperationTypeToUnion()
        self.clipper.SetClipFunction(self.region)
        self.clipper.InsideOutOn()

        selectMapper = vtk.vtkPolyDataMapper()
        selectMapper.SetInput(self.clipper.GetOutput())
        selectMapper.ScalarVisibilityOff()
        self.selectActor.SetMapper(selectMapper)
        self.selectActor.GetProperty().SetColor(0, 1, 0)
        self.selectActor.VisibilityOff()
        self.selectActor.SetScale(1.01, 1.01, 1.01)
        
        if self.colors is not None:
            pntmapper.SetLookupTable(self.lut)
        pntmapper.SetInput(apd.GetOutput())
        pntmapper.SetScalarRange(0, self.maxcolor)
        # create and add actor of mapper to renderer
        pntactor = vtk.vtkLODActor()
        # pntactor.GetProperty().SetColor(1,0,0)
        pntactor.SetMapper(pntmapper)
        pntactor.VisibilityOn()

        # create axes
        axes = vtk.vtkAxes()
        axes.SetOrigin(0,0,0)
        axes.SetScaleFactor(numpy.max(self.data))
        axesTubes = vtk.vtkTubeFilter()
        axesTubes.SetInput(axes.GetOutput())
        axesTubes.SetRadius(axes.GetScaleFactor()/200.0)
        axesTubes.SetNumberOfSides(6)
        #create axes mapper
        axesmapper = vtk.vtkPolyDataMapper()
        axesmapper.SetInput(axesTubes.GetOutput())
        #create actor and add to renderer
        axesactor = vtk.vtkActor()
        axesactor.SetMapper(axesmapper)

        #create labels
        sf = axes.GetScaleFactor()
        xactor = self.BuildLabelActor(self.radioX.GetString(x), {})
        xactor.SetScale(0.075*sf, 0.075*sf, 0.075*sf)
        xactor.SetPosition(0.2*sf, 0.05*sf, -0.05*sf)
        xactor.GetProperty().SetColor(0, 0, 0)

        yactor = self.BuildLabelActor(self.radioY.GetString(y), {'RotateZ': 90})
        yactor.SetScale(0.075*sf, 0.075*sf, 0.075*sf)
        yactor.SetPosition(-0.05*sf, 0.2*sf, -0.05*sf)
        yactor.GetProperty().SetColor(0, 0, 0)

        zactor = self.BuildLabelActor(self.radioZ.GetString(z), {'RotateY': 90})
        zactor.SetScale(0.075*sf, 0.075*sf, 0.075*sf)
        zactor.SetPosition(-0.05*sf, 0.05*sf, 0.6*sf)
        zactor.GetProperty().SetColor(0, 0, 0)

        self.ren.AddActor(xactor)
        self.ren.AddActor(yactor)
        self.ren.AddActor(zactor)

        self.ren.AddActor(axesactor)
        self.ren.AddActor(pntactor)
        self.ren.AddActor(self.selectActor)

        self.widget.Update()
        
        self.ren.ResetCamera()
        
    def Plot(self):
        if self.model.ready:
            # scale data since vtkAxes do not appear 
            # to be independently scaleable
            data = self.model.GetCurrentData()[:]
            for i in range(data.shape[1]):
                top = numpy.max(data[:, i])
                bot = numpy.min(data[:, i])
                data[:, i] = (data[:, i] - bot)/(top - bot)
            self.data = data

            if self.model.IsZ():
                self.colors = numpy.array(self.model.GetCurrentZ()[:], 'i')
                self.colorGate.Enable(True)
            else:
                self.colors = None
            self.ClearBoxes()
            self.RadioButtons(self.model.GetCurrentData().getAttr('fields'))
            self.BuildColors()                
            self.UpdateVTKWindow(self.radioX.GetSelection(),
                         self.radioY.GetSelection(),
                         self.radioZ.GetSelection())

    def OnControlSwitch(self,event):
        self.UpdateVTKWindow(self.radioX.GetSelection(),
                             self.radioY.GetSelection(),
                             self.radioZ.GetSelection())
        self.ClearBoxes()
        self.widget.Render()
    
    def ModelUpdate(self,model):
        self.model = model
        
    def DisableColors(self,event):
        self.UpdateVTKWindow(self.radioX.GetSelection(),
                             self.radioY.GetSelection(),
                             self.radioZ.GetSelection())

    def Gate(self, event):

        clipped = self.clipper.GetOutput()
        pnts = clipped.GetPoints()
        x,y,z = (self.radioX.GetSelection(), self.radioY.GetSelection(), self.radioZ.GetSelection())
        match = []
        newdata = {}
        for j in xrange(0, self.data.shape[0]):
            newdata[(self.data[j,x], self.data[j,y], self.data[j,z])] = j
        for i in xrange(0, pnts.GetNumberOfPoints()):
            match.append(newdata[pnts.GetPoint(i)])
        filtered = numpy.array(map(lambda x: self.data[x], match))
        self.model.updateHDF('GatedData', filtered, self.model.GetCurrentData())

    def GateByColor(self, event):
        fields = self.model.GetCurrentData().getAttr('fields')
        results = []
        z = []
        for i in xrange(0, self.data.shape[0]):
            if self.cbs[self.colors[i]].IsChecked():     
                results.append(self.data[i,:])
                z.append(self.colors[i])
        filtered = numpy.array(results)
        newgroup = self.model.NewGroup('GatedByColor')
        self.model.NewArray('data',filtered, parent=newgroup)
        self.model.current_array.setAttr('fields', fields)
        self.model.hdf5.createArray(self.model.current_group, 'z', numpy.array(z))
        self.model.update()
