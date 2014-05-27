"""Functions to handle plugins"""
import glob
import sys
import os

class Statistics(object):
    pass

class Projections(object):
    pass

class Transform(object):
    pass

def unique(ls):
    """Return unique items from sequece ls. Items must be hashable."""
    return dict.fromkeys(ls).keys()

def init_module(file_list):
    """Create an __init__.py file in every directory that contains a file from filelist."""
    dir_list = unique([os.path.dirname(f) for f in file_list if not f.startswith('__')])
    for d in dir_list:
        open(os.path.join(d, '__init__.py'), 'a').close()

def import_modules(name):
    """Import module corresponding to name and return bottom level module."""
    if name.startswith('__'):
        return
    else:
        s = name.replace('.py', '').replace(os.path.sep, '.')
        a = __import__(s)
        for i in s.split(".")[1:]:
            a = getattr(a, i)
        return a

def addMethod(self, method, name=None):
    """attach a new method to a class
    addMethod(method, name=None) 
    """
    if name is None: name = method.func_name
    class new(self.__class__): pass #IGNORE:C0111
    setattr(new, name, method)
    self.__class__ = new

def get_file_list(dir):
    sys.path.extend(glob.glob(os.path.join(dir, '*/'.replace("/", os.path.sep))))
    file_list = glob.glob(os.path.join(dir, '*/Main.py'.replace("/", os.path.sep)))
    file_list.extend(glob.glob(os.path.join(dir, '*.py'.replace("/", os.path.sep))))
    return file_list

def loadOpen(dir):
    """Loads file io read plugins
    loadOpen(string) -> ({ name : description },{ name : method })
    """
    dir = dir.replace("/", os.path.sep)
    methods = {}
    descriptions = {}
    filters = {}
    styles = {}
    file_list = get_file_list(dir)
    init_module(file_list)

    for match in file_list:
        try:
            a = import_modules(match)

            for b in a.__dict__.keys():
                if b.startswith('_'):
                    pass
                elif b == 'FlowModel':
                    pass
                else:
                    if a.__dict__[b].__class__ == type:
                        if str(a.__dict__[b].__base__) == "<class 'flowio.Io'>":
                            if a.__dict__[b].type in ('Read', 'Write'):
                                name, desc =  a.__dict__[b].newMethods
                                filters[name] = a.__dict__[b].supported
                                descriptions[name]=desc
                            
                                methods[name]= a.__dict__[b].__dict__[name]
                            if a.__dict__[b].type == 'Read':
                                styles[name] = 'open'
                            else:
                                styles[name] = 'save'
        except Exception, e:
            print "failed to load plugin " + str(match) + ": " + str(e)
    return (descriptions, methods, filters, styles)
                
def loadFrames(dir):
    """Loads vizualization plugins
    loadFrames(dir) -> -> { name : method }
    """
    dir = dir.replace("/", os.path.sep)
    frames = {}
    file_list = get_file_list(dir)
    init_module(file_list)

    for match in file_list:
        try:
            a = import_modules(match)
            for b in a.__dict__.keys():
                if b.startswith('_'):
                    pass
                elif b == 'VizFrame':
                    pass
                else:
                    if a.__dict__[b].__class__ == type:
                        if str(a.__dict__[b].__base__) == "<class 'VizFrame.VizFrame'>":
                            frames[a.__dict__[b].type] = a.__dict__[b]
        except Exception, e:
            print "failed to load plugin " + str(match) + ": " + str(e)
    return frames

def loadstatistics(dir):
    """Loads Statistics Plugins
    loadstatistics(string) -> { string : method }
    """
    dir = dir.replace("/", os.path.sep)
    statistics = {}
    file_list = get_file_list(dir)
    init_module(file_list)

    for match in file_list:
        try:
            a = import_modules(match)

            for b in a.__dict__.keys():
                if b.startswith('_'):
                    pass
                elif b == 'Statistics':
                    pass
                else:
                    if a.__dict__[b].__class__ == type:
                        if str(a.__dict__[b].__base__) == "<class 'plugin.Statistics'>":
                            statistics[a.__dict__[b].name] = a.__dict__[b]
        except Exception, e:
            print "failed to load plugin " + str(match) + ": " + str(e)
    return statistics

def loadprojections(dir):
    """loads projection plugins
    loadprojections(dir) -> { name : method }
    """
    dir = dir.replace("/", os.path.sep)
    projections = {}
    file_list = get_file_list(dir)
    init_module(file_list)

    for match in file_list:
        try:
            a = import_modules(match)
    
            for b in a.__dict__.keys():
                if b.startswith('_'):
                    pass
                elif b == 'Projection':
                    pass
                else:
                    if a.__dict__[b].__class__ == type:
                        if str(a.__dict__[b].__base__) == "<class 'plugin.Projections'>":
                            projections[a.__dict__[b].name] = a.__dict__[b]
        except Exception, e:
            print "failed to load plugin " + str(match) + ": " + str(e)
    return projections

if __name__ == '__main__':
    print loadOpen('plugins/io')
    print loadstatistics('plugins/statistics')
    print loadFrames('plugins/visual')
    print loadprojections('plugins/projections')
