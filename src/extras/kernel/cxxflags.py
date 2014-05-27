def hostname():
    try:
        return open('/etc/hostname').read().strip()
    except:
        return ''

def test_env_core_duo():
    return '-march=prescott'

def test_env_opteron():
    return '-march=opteron'

def test_env_pentium_m():
    return '-march=pentium-m -msse2 '

test_env_dict = {'koch':test_env_core_duo, 'pasteur':test_env_opteron,
                 'orpheus':test_env_opteron, 'galen':test_env_opteron,
                 'orwell':test_env_opteron, 'milstein':test_env_opteron,
                 'xinguo':test_env_opteron, 'dbldbl':test_env_core_duo,
                 'poincare':test_env_pentium_m, 'chimp-dulci':test_env_opteron}

def test_env_cxxflags():
    try:
        return '-Wall -pipe -O3 -ffast-math ' + test_env_dict[hostname()]()
    except KeyError:
        print "Using generic optimization flags..."
        return '-Wall -pipe -O3 -ffast-math '
    
def boost_python_env_cxxflags():
    return '-ftemplate-depth-100 -fPIC ' + test_env_cxxflags()
