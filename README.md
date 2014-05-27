Installation on Debian/Ubuntu
----------------------------------------

Flow is an open source GUI for the analysis of flow cytometry data, written in Python with the wxPython toolkit. It is no longer actively maintained,


[[ Base system ]]
sudo apt-get install python-wxgtk2.6 python-numpy python-tables python-scipy python-matplotlib python-networkx python-mdp

[[ Plugins ]]

[ Graphics/ThreeDFrame ]
sudo apt-get install python-vtk

[ Statistics/kmeans ]
sudo apt-get install python-biopython

[ Statistics/Kde and Statistics/bayes ]
sudo apt-get install scons libboost-dev r-mathlib blitz++ lapack3-dev

# install the ANN library (for kde)
cd /tmp
wget http://www.cs.umd.edu/~mount/ANN/Files/1.1.1/ann_1.1.1.tar.gz
tar -xzf ann_1.1.1.tar.gz
cd ann_1.1.1/
make linux-g++
cd ..
sudo mv ann_1.1.1 /usr/local/src

# install the boost numeric binding headers (for bayes)
cd /tmp
wget http://news.tiker.net/news.tiker.net/download/software/boost-bindings/boost-bindings-20070826.tar.gz
tar -xzf boost-bindings-20070826.tar.gz
sudo cp -R boost-bindings/boost/numeric/bindings/ /usr/include/boost/numeric/

# alternatively, check out svn repository of boost-sandbox
svn co http://svn.boost.org/svn/boost/sandbox/boost/numeric/bindings ublas_extensions/boost/numeric/bindings
sudo cp -R ublas_extensions/boost/numeric/bindings/ /usr/include/boost/numeric/

# build the python shared libraries for kde and Bayes where $FLOW is the base directory
sudo apt-get install libboost-python-dev
cd $FLOW/src
scons install

[ Projections/ica ]
sudo apt-get install python-rpy r-base gfortran
sudo R
> install.packages("fastICA")
> q()

# python-rpy binaries are tied to specific R versions
# if the version from the package manager fails (e.g. on Ubuntu 8.02)
# uninstall and install from source
sudo apt-get remove python-rpy
cd /tmp
wget superb-west.dl.sourceforge.net/sourceforge/rpy/rpy-1.02.tar.gz
tar -xzf rpy-1.0.2.tar.gz
cd rpy-1.0.2
python setup.py build
python setup.py install

[Projections/ica2 and pca2 using the Python Modular toolkit]
# available for Debian lenny and sid
sudo apt-get install python-mdp

# all other distributions
Download tar.gz file from sourceforge http://sourceforge.net/project/showfiles.php?group_id=116959
tar -xzf MDP-2.3.tar.gz
sudo python setup.py install

# Flow should now be ready to run
cd $FLOW/src
python App.py

Fedora Core 9 installation
==========================

Packages available using yum
-----------------------------
sudo yum install numpy scipy matplotlib hdf5-devel wxPython vtk-python python-setuptools R R-devel rpy

Packages to install from source
-------------------------------

1. pytables
mkdir src
cd src
wget http://www.pytables.org/download/stable/pytables-2.0.4.tar.gz
tar xzf pytables-2.0.4.tar.gz
cd pytables-2.0.4
python setup.py build_ext --inplace
sudo python setup.py install
exit
cd ..

2. networkx
wget https://networkx.lanl.gov/download/network/networkx-0.37.tar.gz
tar -xzf networkx-0.37.tar.gz
cd networkx-0.37
python seutp.py build
sudo python setup.py install
exit
cd ..

3. MDP
wget http://voxel.dl.sourceforge.net/sourceforge/mdp-toolkit/MDP-2.3.tar.gz
tar xvf MDP-2.3.tar.gz
cd MDP-2.3
python setup.py build
sudo python setup.py install
exit
cd ..

4. PyCluster
wget http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/cluster/Pycluster-1.41.tar.gz
tar xzf Pycluster-1.41.tar.tz
cd Pycluster-1.41

5. fastICA using R (optional but useful as an example of R integration)
sudo yum install gcc-gfortran
R
> install.packages('fastICA')
Follow prompts and quit when done

Download and run Flow
---------------------

wget http://hg.dulci.org/flow/archive/tip.tar.gz
tar xzf tip.tar.gz
cd flow-xxxxxxxxxxxxxx (where xxxxxxxxxxxxxx is some machine-assigned label)
cd src
python App.py


OpenSUSE 10.3 64-bit installation
=================================

Add the following repositories to YAST (or other package management tool)
------------------------------------------------------------------------

http://download.opensuse.org/repositories/science/openSUSE_10.3/
http://software.opensuse.org/download/repositories/science/openSUSE_10.3/

Install the following using YAST (or other package management tool)
------------------------------------------------------------------

gcc gcc-c++ make python-numpy python-scipy python-setuptools
python-tables python-wxgtk python-matplotlib python-matplotlib-wx
R-base

Install the following python packages using setuptools
------------------------------------------------------

sudo easy_install networkx

Install the following from source
---------------------------------

# python Cluster library
 wget http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/cluster/Pycluster-1.41.tar.gz
tar -xzf Pycluster-1.41.tar.gz
cd Pycluster-1.41/
sudo python setup.py install

# R fastICA library
R

# ANN library (for kde)
cd /tmp
wget http://www.cs.umd.edu/~mount/ANN/Files/1.1.1/ann_1.1.1.tar.gz
tar -xzf ann_1.1.1.tar.gz
cd ann_1.1.1/
make linux-g++
cd ..
sudo mv ann_1.1.1 /usr/local/src

# python MDP library
wget http://voxel.dl.sourceforge.net/sourceforge/mdp-toolkit/MDP-2.3.tar.gz
tar -xzf MDP-2.3.tar.gz
sudo python setup.py install

# VTK (python bindings do not appear to work in 64-bit openSUSE 10.3)
wget http://www.vtk.org/files/release/5.2/vtkdata-5.2.0.tar.gz
tar -xzf vtkdata-5.2.0.tar.gz
wget http://www.vtk.org/files/release/5.2/vtk-5.2.0.tar.gz
tar -xzf vtk-5.2.0.tar.gz
mkdir VTKBuild
cd VTKBuild
ccmake ../VTK (set the options as shown)
 BUILD_EXAMPLES                   ON
 BUILD_SHARED_LIBS                ON
 BUILD_TESTING                    OFF
 CMAKE_BACKWARDS_COMPATIBILITY    2.4
 CMAKE_BUILD_TYPE
 CMAKE_INSTALL_PREFIX             /usr/local
 VTK_DATA_ROOT                    < VTKData location - auto-detected >
 VTK_USE_INFOVIS                  ON
 VTK_USE_PARALLEL                 OFF
 VTK_USE_RENDERING                ON
 VTK_USE_VIEWS                    ON
 VTK_WRAP_JAVA                    OFF
 VTK_WRAP_PYTHON                  ON
 VTK_WRAP_TCL                     OFF
make
sudo make install




Mac OS X 10.5  installation
=====================

[[ Base system ]]

Download and install the wxPython binary from http://www.wxpython.org/

Install the binaries for scipy, numpy and matplotlib from
http://pythonmac.org/packages/py25-fat/index.html

cd /tmp
wget http://pypi.python.org/packages/source/n/networkx/networkx-0.36.tar.gz
tar -xzf networkx-0.36.tar.gz
cd networkx-0.36
python setup.py build
sudo python setup.py install

cd /tmp
wget http://www.pytables.org/download/stable/pytables-2.0.3.tar.gz
tar -xzf pytables-2.0.3.tar.gz
cd pytables-2.0.3
python setup.py build
sudo python setup.py install


[[ Plugins ]]

[ Graphics/ThreeDFrame ]

* Installing cmake
cd /tmp
wget http://www.cmake.org/files/v2.4/cmake-2.4.8.tar.gz
tar -xzf cmake-2.4.8.tar.gz
cd cmake-2.4.8
./bootstrap
make
sudo make install

* Installing VTK
cd /tmp
cvs -d :pserver:anonymous@public.kitware.com:/cvsroot/VTK login
(respond with password vtk)
cvs -d :pserver:anonymous@public.kitware.com:/cvsroot/VTK checkout VTK
mkdir VTKBuild
cd VTKBuild
ccmake ../VTK
options (BUILD_SHARED_LIBS ON; VTK_WRAP_PYTHON ON)
Hit 'c' to configure and 'g' to generate Makefiles
make
sudo make install
cd Wrapping/Python
python setup.py build
sudo python setup.py install
export PYTHONPATH=/Library/Python/2.5/site-packages/VTK-5.1.0-py2.5.egg/vtk

[ Statistics/kmeans ]
wget http://downloads.sourceforge.net/numpy/Numeric-24.2.tar.gz

[ Statistics/Kde and Statistics/bayes ]

# install the ANN library (for kde)
cd /tmp
wget http://www.cs.umd.edu/~mount/ANN/Files/1.1.1/ann_1.1.1.tar.gz
tar -xzf ann_1.1.1.tar.gz
cd ann_1.1.1/
make macosx-g++
cd ..
sudo mv ann_1.1.1 /usr/local/src

# install the blitz++ library
cd /tmp
wget http://internap.dl.sourceforge.net/sourceforge/blitz/blitz-0.9.tar.gz
tar -xzf blitz-0.9.tar.gz
cd blitz-0.9
./configure
make
sudo make install

# install the C++ boost library
cd /tmp
wget http://superb-west.dl.sourceforge.net/sourceforge/boost/boost_1_35_0.tar.gz
tar -xzf boost_1_35_0.tar.gz
cd boost_1_35_0
./configure
make
sudo make install

# install the boost numeric binding headers (for bayes)
cd /tmp
wget http://mathema.tician.de/news.tiker.net/download/software/boost-numeric-bindings/boost-numeric-bindings-20081116.tar.gz
tar xzf boost-numeric-bindings-20081116.tar.gz
sudo cp -R boost-bindings/boost/numeric/bindings/ /usr/include/boost/numeric/

# alternatively, check out svn repository of boost-sandbox
cd /tmp
svn co http://svn.boost.org/svn/boost/sandbox/boost/numeric/bindings ublas_extensions/boost/numeric/bindings
sudo cp -R ublas_extensions/boost/numeric/bindings/ /usr/include/boost/numeric/

# build the python shared libraries for kde and Bayes where $FLOW is the base directory
cd $FLOW/src
scons install

[ Projections/ica ]

# Install R from source
cd /tmp
wget http://cran.r-project.org/src/base/R-2/R-2.6.2.tar.gz
tar -xzf R-2.6.2.tar.gz
cd R-2.6.2.tar.gz
./configure --enable-BLAS-shlib --with-blas='-framework vecLib'
make
sudo make install
cd src/nmath/standalone
make
sudo ln -s /Library/Frameworks/R.framework/Resources/R /usr/local/bin/R

# Install fastICA
sudo R
> install.packages("fastICA")

# Install rpy
cd /tmp
wget superb-west.dl.sourceforge.net/sourceforge/rpy/rpy-1.02.tar.gz
tar -xzf rpy-1.0.2.tar.gz
cd rpy-1.0.2
python setup.py build
python setup.py install

[Projections/ica2 and pca2 using the Python Modular toolkit]
Download tar.gz file from sourceforge http://sourceforge.net/project/showfiles.php?group_id=116959
tar -xzf MDP-2.3.tar.gz
sudo python setup.py install

Windows Installation
====================

Note - this was done on a Windows Vista Business Machine with User
Access Control (UAC) turned off.

The following binaries have nice Windows installers

Download and install the Enthought binary from http://www.enthought.com/products/epddownload.php
Download and install Numeric binary from http://biopython.org/DIST/Numeric-24.2.win32-py2.5.exe
Download and install PyCluster binary from http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/cluster/Pycluster-1.39.win32-py2.5.exe
Download and install Networkx binary from http://pypi.python.org/packages/any/n/networkx/networkx-0.36.win32.exe

Add Python to the Environment path by clicking on the Start icon, then
right-clicking on Computer and then "Advanced system settings" on the
Tasks pane which will open a System Properties dialog. Click "Environment Variables" and edit "System variables" and add

 ;C:\Python25;C:\Python25\Scripts

to the end of the Path string.

== Optional install of MDP for ICA and PCA functionality ==
MDP also has a Windows binary at
http://downloads.sourceforge.net/mdp-toolkit, but the link was down
when I tried it. If it works for you, install the binary.

If not , download MDP from
http://downloads.sourceforge.net/mdp-toolkit/MDP-2.3.zip

Unzip into an appropriate directory, open a Command Prompt, navigate
to the MDP-23 folder and type "python setup.py install"

== Note ==
Executables for Windows 32 and 64 bit DLLs need to be provided, and the Scons script modified to include a section for Windows installations.
