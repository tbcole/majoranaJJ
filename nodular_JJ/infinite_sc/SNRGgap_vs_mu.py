import sys
import time
import os
import gc

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import majoranaJJ.modules.SNRG as SNRG
import majoranaJJ.modules.finders as finders
import majoranaJJ.modules.checkers as check
import majoranaJJ.modules.constants as const
import scipy.interpolate as interp
###################################################
#Defining System
ax = 50 #lattice spacing in x-direction: [A]
ay = 50 #lattice spacing in y-direction: [A]
Nx = 10 #Number of lattice sites along x-direction
Wj = 600 #Junction region [A]
nodx = 2 #width of nodule
nody = 5 #height of nodule
#new_params  = check.junction_geometry_check(Nx, 1000, nodx, nody, int(Wj/ay))
#Nx = new_params[0]
#nodx = new_params[2]
print(Nx, nodx)
Lx = Nx*ax
Junc_width = Wj*.1 #nm
Nod_widthx = nodx*ay*.1 #nm
Nod_widthy = nody*ay*.1 #nm

print("Nodule Width in x-direction = ", Nod_widthx, "(nm)")
print("Nodule Width in y-direction = ", Nod_widthy, "(nm)")
print("Junction Width = ", Junc_width, "(nm)")
#########################################
#Defining Hamiltonian parameters
alpha = 200 #Spin-Orbit Coupling constant: [meV*A]
phi = 0*np.pi #SC phase difference
delta = 0.30 #Superconducting Gap: [meV]
Vj = -30 #Junction potential: [meV]
gx = 1 #mev

mu_i = 1
mu_f = 4
delta_mu = mu_f - mu_i
res = 0.01
steps = int(abs(delta_mu/res))+1
mu = np.linspace(mu_i, mu_f, steps) #meV

print("alpha = ", alpha)
print("Mu_i = ", mu_i)
print("Mu_f = ", mu_f)
print("Gamma_x = ", gx)
print("Vj = ", Vj)
print()
###################################################
dirS = 'gap_data'
if not os.path.exists(dirS):
    os.makedirs(dirS)
try:
    PLOT = str(sys.argv[1])
except:
    PLOT = 'F'
if PLOT != 'P':
    gap = np.zeros(mu.shape[0])
    np.save("%s/mu Wj = %.1f nm Lx = %.1f nm nodx = %.1f nm nody = %.1f nm Vj = %.1f meV alpha = %.1f meVA delta = %.2f meV phi = %.2f mu_i = %.1f meV mu_f = %.1f meV gx = %.2f meV.npy" % (dirS, Junc_width, Lx*.1, Nod_widthx,  Nod_widthy, Vj,  alpha, delta, phi, mu_i, mu_f, gx), mu)
    for i in range(mu.shape[0]):
        print(steps-i, "| mu =", mu[i])
        gap[i] = SNRG.gap(Wj=Wj, Lx=Lx, nodx=nodx, nody=nody, ax=ax, ay=ay, gam=gx, mu=mu[i], Vj=Vj, alpha=alpha, delta=delta, phi=phi, targ_steps=1000, n_avg=3, muf=mu[i], PLOT=False, tol=1e-8)[0]

        np.save("%s/gapfxmu Wj = %.1f nm Lx = %.1f nm nodx = %.1f nm nody = %.1f nm Vj = %.1f meV alpha = %.1f meVA delta = %.2f meV phi = %.2f mu_i = %.1f meV mu_f = %.1f meV gx = %.2f meV.npy" % (dirS, Junc_width, Lx*.1, Nod_widthx,  Nod_widthy, Vj,  alpha, delta, phi, mu_i, mu_f, gx), gap)
        gc.collect()

    sys.exit()
else:
    gap = np.load("%s/gapfxmu Wj = %.1f nm Lx = %.1f nm nodx = %.1f nm nody = %.1f nm Vj = %.1f meV alpha = %.1f meVA delta = %.2f meV phi = %.2f mu_i = %.1f meV mu_f = %.1f meV gx = %.2f meV.npy" % (dirS, Junc_width, Lx*.1, Nod_widthx,  Nod_widthy, Vj, alpha, delta, phi, mu_i, mu_f, gx))

    mu = np.load("%s/mu Wj = %.1f nm Lx = %.1f nm nodx = %.1f nm nody = %.1f nm Vj = %.1f meV alpha = %.1f meVA delta = %.2f meV phi = %.2f mu_i = %.1f meV mu_f = %.1f meV gx = %.2f meV.npy" % (dirS, Junc_width, Lx*.1, Nod_widthx,  Nod_widthy, Vj, alpha, delta, phi, mu_i, mu_f, gx))

    spl = interp.splrep(mu, gap/delta)
    mu_new = np.linspace(mu_i, mu_f, mu.shape[0]*10)
    gap_new = interp.splev(mu_new, spl)

    plt.grid()

    plt.scatter(mu, gap/delta, c='r', zorder=2, s=2)
    #plt.plot(mu_new, gap_new, c='b', lw=2, zorder=1)
    plt.plot(mu, gap/delta, c='b', lw=2, zorder=1)


    plt.xlabel(r'$\mu$ (meV)')
    plt.ylabel(r'$\Delta_{qp}/\Delta_{0}$')
    #plt.ylim(0,0.3)

    #plt.subplots_adjust(top=0.75, left=0.25, bottom=0.25)
    title = r'gx = {} Lx = {} nm, lx = {} nm, W1 = {} nm, W2 = {} nm, Vj = {} meV'.format(gx, Lx*.1, Nod_widthx, Junc_width, Junc_width-2*Nod_widthy, Vj)
    plt.title(title, loc = 'center', wrap = True)
    #plt.savefig('gapfxmu juncwidth = {} nodwidthx = {} nodwidthy = {} alpha = {} phi = {} Vj = {}.png'.format(Junc_width, Nod_widthx, Nod_widthy, alpha, phi, Vj), dpi=700)
    plt.show()

    sys.exit()
