import sys
import time
import os
import gc

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.signal import argrelextrema
import scipy.linalg as LA
import scipy.sparse.linalg as spLA

import majoranaJJ.operators.sparse_operators as spop #sparse operators
from majoranaJJ.operators.potentials import Vjj #potential JJ
import majoranaJJ.lattice.nbrs as nb #neighbor arrays
import majoranaJJ.lattice.shapes as shps #lattice shapes
import majoranaJJ.modules.plots as plots #plotting functions
import majoranaJJ.modules.gamfinder as gamfinder
from majoranaJJ.modules.checkers import boundary_check as bc
import majoranaJJ.modules.checkers as check
###################################################
#Defining System
Nx = 3 #Number of lattice sites along x-direction
Ny = 50 #Number of lattice sites along y-direction
ax = 100 #lattice spacing in x-direction: [A]
ay = 100 #lattice spacing in y-direction: [A]
Wj = 10 #Junction region
cutx = 0 #width of nodule
cuty = 0 #height of nodule
Nx, Ny, cutx, cuty, Wj = check.junction_geometry_check(Ny, Nx, Wj, cutx, cuty)
print("Nx = {}, Ny = {}, cutx = {}, cuty = {}, Wj = {}".format(Ny, Nx, Wj, cutx, cuty))

Junc_width = Wj*ay*.10 #nm
SC_width = ((Ny - Wj)*ay*.10)/2 #nm
Nod_widthx = cutx*ax*.1 #nm
Nod_widthy = cuty*ay*.1 #nm
print("Nodule Width in x-direction = ", Nod_widthx, "(nm)")
print("Nodule Width in y-direction = ", Nod_widthy, "(nm)")
print("Junction Width = ", Junc_width, "(nm)")
print("Supercondicting Lead Width = ", SC_width, "(nm)")
###################################################coor = shps.square(Nx, Ny) #square lattice
coor = shps.square(Nx, Ny) #square lattice
NN = nb.NN_Arr(coor) #neighbor array
NNb = nb.Bound_Arr(coor) #boundary array
lat_size = coor.shape[0]
print("Lattice Size: ", lat_size)

Lx = (max(coor[:, 0]) - min(coor[:, 0]) + 1)*ax #Unit cell size in x-direction
Ly = (max(coor[:, 1]) - min(coor[:, 1]) + 1)*ay #Unit cell size in y-direction
###################################################
#Hamiltonian Parameters
alpha = 100 #Spin-Orbit Coupling constant: [meV*A]
gx = 0.9 #parallel to junction: [meV]
phi = 0 #SC phase difference
delta = 1.0 #Superconducting Gap: [meV]
mu = 10  #Chemical Potential: [meV]
#####################################
k = 24 #This is the number of eigenvalues and eigenvectors you want
steps = 51 #Number of kx values that are evaluated
qx = np.linspace(0, np.pi/Lx, steps) #kx in the first Brillouin zone

bands = np.zeros((steps, k))
start = time.perf_counter()
for i in range(steps):
    print(steps - i)
    H = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, mu=mu, alpha=alpha, delta=delta, phi=phi, gamx=gx, qx=qx[i])
    eigs, vecs = spLA.eigsh(H, k=k, sigma=0, which='LM')
    idx_sort = np.argsort(eigs)
    eigs = eigs[idx_sort]
    bands[i, :] = eigs

end = time.perf_counter()
print("Time: ", end-start)

for i in range(bands.shape[1]):
    plt.plot(qx, bands[:, i], c ='mediumblue', linestyle = 'solid')
    plt.plot(-qx, bands[:, i], c ='mediumblue', linestyle = 'solid')
    #plt.scatter(q, eigarr[:, i], c ='b')
plt.plot(qx, 0*qx, c = 'k', linestyle='solid', lw=1)
plt.plot(-qx, 0*qx, c = 'k', linestyle='solid', lw=1)
#plt.xticks(np.linspace(min(k), max(k), 3), ('-π/Lx', '0', 'π/Lx'))
plt.xlabel('kx (1/A)')
plt.ylabel('Energy (meV)')
plt.title('BDG Spectrum', wrap = True)
plt.savefig('juncwidth = {} SCwidth = {} nodwidthx = {} nodwidthy = {} Delta = {} Alpha = {} phi = {} mu = {}.png'.format(Junc_width, SC_width, Nod_widthx, Nod_widthy, delta, alpha, phi, mu))
plt.show()

#####################################
"""
#VV = sparse.bmat([[None, V], [-V, None]], format='csc', dtype='complex')
#plots.junction(coor, VV, title = 'Potential Profile', savenm = 'potential_profile.jpg')

k = 26
H = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, alpha=alpha, delta=delta, phi = phi, V=V, gammax=gx, gammaz=gz, mu=mu, qx=0.00287, periodicX=True, periodicY=False)

eigs, vecs = spLA.eigsh(H, k=k, sigma=0, which='LM')
idx_sort = np.argsort(eigs)
eigs = eigs[idx_sort]
vecs = vecs[:, idx_sort]
print(eigs)

n = int(k/2)
plots.state_cmap(coor, eigs, vecs, n = int(k/2), title = r'$|\psi|^2$', savenm = 'State_k={}.png'.format(n))

sys.exit()

for i in range(int(k/2), k):
    plots.state_cmap(coor, eigs, vecs, n = i, title = r'$|\psi|^2$', savenm = 'State_k={}.png'.format(i))
"""