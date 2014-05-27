import commands
SConscript('src/SConscript')

def pyversion():
    pystr = commands.getoutput('python -V')
    version = pystr.split(' ')[1]
    major, minor = version.split('.')[:2]
    return major + '.' + minor


# Install files with "scons DESTDIR=install_dir install".
opts = Options()
opts.AddOptions(('DESTDIR', 'Base path for installed files', ''), ('PREFIX', 'The root of the installation tree.', '/usr/local'))
install_env = Environment(options=opts)
install_env.Alias('install', install_env.Install(dir = '${DESTDIR}/${PREFIX}/lib/python'+pyversion()+'/site-packages', source=['src/extras/bayes/bayes.so']))


#SConscript(['src/extras/bayes/SConscript'], 'install_env')

Alias('all', '.')
