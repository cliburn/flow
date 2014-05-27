"""model component of our MVC structure"""
from numpy import array, where, greater, min, max, take, reshape
from numpy.random import shuffle, randint
from numpy.linalg import solve
import os
import tables
from tempfile import NamedTemporaryFile
from transforms import ScaleOp, ClipOp, LinearOp, QuadraticOp, LogOp, LognOp, BiexponentialOp, LogicleOp, HyperlogOp, ArcsinhOp, NormalScaleOp

class AbstractModel(object):
    """abstraction of basic model"""
    def __init__(self): #IGNORE:C0103
        self.listeners = []
    
    def addListener(self, listenerFunc):
        """Attach a listner to the model"""
        self.listeners.append(listenerFunc)
        
    def removeListener(self, listenerFunc):
        """Remove a listener from the model"""
        self.listeners.remove(listenerFunc)
        
    def update(self):
        """update the model's listeners"""
        for eachFunc in self.listeners:
            eachFunc(self)
            
class FlowModel(AbstractModel):
    """Model part of MVC for visualization"""
    def __init__(self):
        super(FlowModel, self).__init__()

        self.ready = False
        # fill out this stuff for temp files and hdf5 stuff.
        self.mode = 'w'
 
        self.current_group = None # self.hdf5.getNode('/', 'data')
        self.newFile()

        # store last saved name
        self.savedAs = None
        # indicator flag for change status
        self.isChanged = False

        # indicator flag for showing components or modes
        self.showMode = False

        # obo file
        self.obofile = 'obo/cell.obo'

        
    def LoadData(self, headers, data, datastr):
        """Create a new array with headers and data."""
        self.ready = False
        data = self.hdf5.createArray(self.GetCurrentGroup(), 'data', data, datastr)
        data.setAttr('fields', headers)
        self.current_array = data
        self.UpdateData()

    def UpdateData(self):
        """Update self.data after some statisticsation."""
        self.ready = True
        self.update()
    
    def NewGroup(self, name, parent=None):
        """
        creates a new set of data in the hdf5 file
        NewGour(name = string, <parent = group | current group>)
        """
        if parent is None:
            parent = self.current_group
        newName = self.checkName(name, group=parent)
        self.current_group = self.hdf5.createGroup(parent, newName) #IGNORE:E1101
        self.isChanged = True
    
    def NewArray(self, name, array, parent=None, overwrite=False):
        """
        create a new array
        NewArray(name = string, array = numpy.array, <parent = group | current group>, overwrite= bool)
        """
        if parent is None:
            parent = self.current_group
        if overwrite:
            newName = name
            try:
                self.hdf5.removeNode(parent, newName) # remove the node if it exists.
            except tables.NoSuchNodeError:
                pass
        else:
            newName = self.checkName(name, group=parent)
        self.current_array = self.hdf5.createArray(parent, newName, array)
        self.update()

    def SelectGroup(self, group):
        """selects the current working data group from the hdf5 file"""
                
        if group._c_classId == "GROUP" and group != self.hdf5.root: #IGNORE:W0212
            self.current_group = group
            self.current_array = self.GetCurrentData()
        elif group._c_classId == "ARRAY": #IGNORE:W0212
            self.current_group = group._v_parent #IGNORE:W0212
            self.current_array = group
        elif group is self.hdf5.root:
            self.current_group = self.hdf5.root
            if hasattr(self.hdf5.root, 'data'):
                self.current_array = self.hdf5.root.data
            else:
                self.current_array = None
        self.isChanged = True
        

    def SelectGroupByPath(self, group):
        """ selecta group via it's path"""
        self.SelectGroup(self.hdf5.getNode(group))
    
    def SelectRoot(self):
        """Reset current selection to root."""
        self.current_group = self.hdf5.root

    def SetGroupParams(self, value):
        group = self.GetCurrentGroup()
        group._v_attrs.params = value
        self.isChanged = True

    def GetCurrentGroup(self):
        """returns current working group from the hdf5 file"""
        return self.current_group
    
    def GetCurrentData(self):
        """returns the current data array"""
        return self._loopForData(self.current_group)
    
    def GetCurrentZ(self, group = None):
        """get current Z for a group if it exists, defaults to the currently selected gorup"""
        if group is None:
            group = self.current_group
        try:
            # print self.current_group
            return self._loopForZ(group)
        except AttributeError:
            return None

    def GetCurrentAnnotation(self):
        """Get the current annotation array"""
        try:
            return self._loopForAnnotation(self.current_group)
        except AttributeError:
            return None

    def GetCurrentHeaders(self):
        """Get headers for channels."""
        try:
            return self.GetCurrentGroup().headers[:]
        except AttributeError:
            return self.GetCurrentData().getAttr('fields')

    def GetHistory(self, node = None):
        '''
        Get the history list of a node
        GetHistory(node = None)
        '''
        if node is None:
            node = self.GetCurrentData()
        try:
            return node.attrs.hist
        except AttributeError:
            node.attrs.hist = []
            return node.attrs.hist 

    def AddHistory(self, hist, node=None):
        if node is None:
            node = self.GetCurrentData()
        try:
            node.attrs.hist
        except AttributeError:
            node.attrs.hist = []
        node.attrs.hist.append(hist)
    
    def SetHistory(self,hist, node=None):
        '''
        set the history list of a node
        SetHistory(hist, node)
        '''
        if node is None:
            node = self.GetCurrentData()
        node.attrs.hist = hist
        self.isChanged = True

    def IsZ(self):
        """is there a current z grouop?"""
        try:
            z = self.GetCurrentZ()
        except AttributeError:
            z = None
        if z is not None:
            return True
        else:
            return False
        
    def SetZLabels(self, z, values):
        z.attrs.labels = values
        self.isChanged = True
        
    def GetZLabels(self, z):
        if z ==  None:
            return ["Color 1"]
        else:
            try:
                return z.attrs.labels
            except:
                # get proportion to put in label
                try:
                    pro = array(self.current_group.pi_end[:])
                    pro = 100*pro/float(sum(pro))
                except AttributeError:
                    pro = [0]*(1+max(z[:]))

                values = []
                for i in range(1, int(max(z[:]))+2):
                    values.append("Color %d (%.2f)" % (i, pro[i-1]))
                z.attrs.labels = values
                return values

    def _loopForData(self, group):
        """walk up tree looking for a data array"""
        try:
            return group.data
        except AttributeError:
            if group == self.hdf5.root:
                raise AttributeError
            else:
                return self._loopForData(group._v_parent) #IGNORE:W0212 #IGNORE:W0702
            
    def _loopForZ(self, group):
        """Walk up tree looking for Z values"""
        try:
            return group.z
        except AttributeError:
            if group == self.hdf5.root:
                raise AttributeError
            else:
                return self._loopForZ(group._v_parent)
    
    def _loopForAnnotation(self, group):
        """Walk up the tree looking for an annotation array"""
        try:
            return group.annotation
        except AttributeError:
            if group == self.hdf5.root:
                raise AttributeError
            else:
                return self._loopForAnnotation(group._v_parent)
            
            
            
    def _loopForSpillover(self, group):
        try:
            return group.spillover
        except AttributeError:
            if group == self.hdf5.root:
                raise AttributeError
            else:
                return self._loopForSpillover(group._v_parent) #IGNORE:W0212 #IGNORE:W0702
        
    def GetMax(self):
        """Returns the max value in the data... may be depreciated"""
        return max(self.GetCurrentData())

    def GetRange(self):
        """Returns max - min of data."""
        data = self.GetCurrentData()[:]
        return max(max(data, 0) - min(data, 0))
    
    def close(self):
        """Close the open hdf5 temp file and remove it"""
        try:
            name = self.hdf5.filename
            self.hdf5.close()
            del self.hdf5
            self.hdf5 = None
            os.remove(name)
        except:
            pass
    
    def isOpen(self):
        """checks if the hdf5 is open, and basically ready"""
        try:
            status = self.hdf5.isopen
        except:
            status = 0
        if status == 1:
            return True
        else:
            return False
    
    def saveAs(self, location):
        """Save the hdf5 file out"""
        if self.isOpen():
            self.hdf5.copyFile(location, overwrite=True)
            self.savedAs=location
            
    def deleteNode(self, node):
        """delete a node from the hdf5 tree"""
        if node == self.hdf5.root:
            pass
        else:
            parent = node._v_parent
            self.SelectGroup(parent)
            node._f_remove(True)
        self.isChanged = True        
        
    def copyNode(self, source, dest, title=None):
        '''copy a node in the hdf5 tree to a new location'''
        source._f_copy(dest, title, True, True)
        
    def newFile(self):
        self.close()
        filename = NamedTemporaryFile().name
        self.hdf5 = tables.openFile(filename, 'w')
        self.current_group = self.hdf5.getNode('/')
        
        self.UpdateData()
        self.isChanged = True
        self.ready = False

    def open(self, hdf5File):
        self.ready = False
        self.close()
        
        name = NamedTemporaryFile().name
        src = tables.openFile(hdf5File,'r')

        src.copyFile(name)

        src.close()
        self.hdf5 = tables.openFile(name,'a')
        try:
            self.current_group = [group for group in self.hdf5.walkGroups('/')][1]
        except IndexError:
            self.current_group = self.hdf5.getNode('/')
            
        self.current_array = self.GetCurrentData()
        self.savedAs = hdf5File
        self.UpdateData()
        self.isChanged = True

    def checkName(self, name, group=None, counter=1):
        if group is None:
            parent = self.GetCurrentGroup()
        else:
            parent = group
        count = counter
        if counter != 1:
            newName = name + " " + str(counter)
        else:
            newName = name
        try:
            group.__getattr__(newName)
            newName = self.checkName(name, group=parent, counter=count+1)
        except AttributeError:
            pass # means we've found a name that doesn't exist
        return newName
                
    def TextInfo(self, item):
        desc = ''
        for attr in item._v_attrs._v_attrnames:
            desc = desc + attr + " = " + str(item._v_attrs.__getattribute__(attr)) + "\n"
        return desc

    def getSpill(self):
        try:
            spill = self._loopForSpillover(self.GetCurrentGroup())
            markers = spill.getAttr('markers')
            return spill, markers
        except:
            return None

    def setSpill(self, spill):
        """Set spillover matrix for dataset."""
        spill = spill.split(',')
        n = int(spill[0])
        headers = spill[1:(n+1)]
        matrix = reshape(map(float, spill[n+1:]), (n, n))
        group = self.GetCurrentGroup()
        try:
            spillover = self._loopForSpillover(group)
            spillover[:] = matrix
        except AttributeError:
            spillover = self.hdf5.createArray(group, 'spillover', matrix)
        spillover.setAttr('markers', headers)
        
    def compensate(self):
        spill = self.getSpill()
        data = self.GetCurrentGroup().data
        if spill:
            comp, markers = spill
            comp = comp[:]
            indices = [data.attrs.fields.index(data.attrs.NtoS[m])
                       for m in markers]
            observed = array([data[:,i] for i in indices])
            compensated = solve(comp.T, observed)
            # switch in place, destructively
            for n, i in enumerate(indices):
                data[:,i] = compensated[n,:]

    def updateHDF(self, group, data, old_data=None, old_group=None, **kwargs):
        if old_data is None:
            old_data = self.GetCurrentData()
        if old_group is None:
            old_group = self.GetCurrentGroup()
        self.NewGroup(group)
        _data = self.hdf5.createArray(self.current_group, 'data', array(data))
        # first copy over old attributes
        for attr in old_data.attrs._f_list('user'):
            _data.setAttr(attr, old_data.getAttr(attr))
        # then overwrite any provided key-value attributes
        for key, value in kwargs.items():
            _data.setAttr(key, value)
        self.current_array = data
        self.update()
        self.isChanged = True

    # put model operations here
    def FilterOnCols(self, group, indices, target=None):
        if target is None:
            target = self.GetCurrentGroup()
        self.current_group = target
        data = take(array(self.GetCurrentData()[:]), indices, axis=1)
        fields = [field for i, field in enumerate(self.GetCurrentData().getAttr('fields')) if i in indices]
        self.updateHDF(group, data, self.GetCurrentData(), fields=fields)

    def FilterOnRows(self, group, indices, target=None):
        if target is None:
            target = self.GetCurrentGroup()
        self.current_group = target
        data = take(array(self.GetCurrentData()[:]), indices, axis=0)
        self.updateHDF(group, data, self.GetCurrentData())
        
    def Transform(self, op, group, indices, inputs, target):
        if target is None:
            target = self.GetCurrentGroup()
        self.current_group = target
        data = array(self.GetCurrentData()[:])
        hist = self.GetHistory()
        op(data, indices, inputs)
        self.updateHDF(group, data, self.GetCurrentData())
        hist.append((group, [indices, inputs]))
        self.AddHistory(hist)
        

    def ScaleTransform(self, indices, inputs, target=None):
        self.Transform(ScaleOp, 'ScaleTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['scale', indices, inputs]

    def NormalScaleTransform(self, indices, inputs, target=None):
        self.Transform(NormalScaleOp, 'NormalScaleTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['normal scale', indices, inputs]

    def ClipTransform(self, indices, inputs, target=None):
        self.Transform(ClipOp, 'ClipTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['clip', indices, inputs]

    def LinearTransform(self, indices, inputs, target=None):
        self.Transform(LinearOp, 'LinearTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['linear', indices, inputs]
    
    def QuadraticTransform(self, indices, inputs, target=None):
        self.Transform(QuadraticOp, 'QuadraticTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['quadratic', indices, inputs]

    def LogTransform(self, indices, inputs, target=None):
        self.Transform(LogOp, 'LogTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['log', indices, inputs]

    def LognTransform(self, indices, inputs, target=None):
        self.Transform(LognOp, 'LognTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['logn', indices, inputs]

    def BiexponentialTransform(self, indices, inputs, target=None):
        self.Transform(BiexponentialOp, 'BiexponentialTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['biexponential', indices, inputs]

    def LogicleTransform(self, indices, inputs, target=None):
        self.Transform(LogicleOp, 'LogicleTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['logicle', indices, inputs]

    def HyperlogTransform(self, indices, inputs, target=None):
        self.Transform(HyperlogOp, 'HyperlogTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['hyperlog', indices, inputs]

    def ArcsinhTransform(self, indices, inputs, target=None):
        self.Transform(ArcsinhOp, 'ArcsinhTransform', indices, inputs, target)
        self.GetCurrentData().attrs.batch=['arcsin', indices, inputs]

    def GetDataGroups(self):
        results = []
        groups = self.hdf5.walkGroups()
        for i in groups:
            if hasattr(i, 'data'):
                results.append(i._v_pathname)
        
        return results
