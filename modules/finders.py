import majoranaJJ.operators.sparse_operators as spop #sparse operators
import majoranaJJ.modules.SNRG as SNRG
import majoranaJJ.operators.potentials as pot
from majoranaJJ.modules import constants as const
import numpy as np
import scipy.linalg as LA
import scipy.sparse.linalg as spLA
from scipy.signal import argrelextrema
import sys
import matplotlib.pyplot as plt

def minima(arr):
    abs_min = min(arr)
    for i in range(arr.shape[0]):
        min_temp = arr[i]
        if min_temp <= abs_min:
            abs_min = min_temp
            idx = i
    return abs_min, idx

def targ_step_finder(res_gap, M, kx_max):
    res_k = res_gap/M
    target_steps = kx_max/res_k
    return target_steps

def step_finder(target_steps, n_avg=7):
    #n_steps makes resolution n_steps/2 times better, e.g. if original steps were 100, n_steps=10, as if og steps were 500
    # average number of minima assume is 7, = n
    # r is target resolution in units of (steps)
    # goal is to find z, minimum number of steps required to reach that resolution
    #two equations are
    # x + ny = z where z is total number of steps for entire calculation
    # xy = 2R
    # ==> y = -1/n x +z/n
    # ==> y = 2r/x
    # multiply both sides of eq 1 by x: x^2 + nxy - xz = 0
    # substitute x^2 - xz + 2nr = 0
    # z(x) = (x^2 + 2nr)/x = x +2nr/x
    # dz/dx = 0 ==> minimize z
    # 1 - 2nr/x^2 = 0 ==> x^2 = 2nr ==> x = sqrt(2nr) ===> y = 2r/sqrt(2nr)

    first_steps = np.sqrt(2*n_avg*target_steps)
    second_steps = 2*target_steps/np.sqrt(2*n_avg*target_steps)
    return int(first_steps), int(second_steps)

#Assuming linear behavior of the E vs gamma energy dispersion
#Taking the slope and the initial points in the energy vs gamma plot
#Extrapolate to find zero energy crossing
def linear_gam_finder(
    coor, ax, ay, NN, mu,
    NNb = None, Wj = 0, cutx = 0, cuty = 0, V = 0,
    gammax = 0, gammay = 0, gammaz = 0,
    alpha = 0, delta = 0 , phi = 0,
    qx = 0, qy = 0, periodicX = True, periodicY = False,
    k = 20, sigma = 0, which = 'LM', tol = 0, maxiter = None
    ):

    #saving the particle energies, all energies above E=0
    Ei = spop.EBDG(
        coor, ax, ay, NN, NNb = NNb, Wj = Wj,
        cutx = cutx, cuty = cuty,
        V = V, mu = mu,
        gammax = gammax, gammay = gammay, gammaz = gammaz,
        alpha = alpha, delta = delta, phi = phi,
        qx = qx, qy = qy,
        periodicX = periodicX, periodicY = periodicY,
        k = k, sigma = sigma, which = which, tol = tol, maxiter = maxiter
        )[int(k/2):][::2]
    #print(Ei)

    deltaG = 0.00001
    gammanew = gammax + deltaG

    #saving the particle energies, all energies above E=0
    Ef = spop.EBDG(
        coor, ax, ay, NN, NNb = NNb, Wj = Wj,
        cutx = cutx, cuty = cuty,
        V = V, mu = mu,
        gammax = gammanew, gammay = gammay, gammaz = gammaz,
        alpha = alpha, delta = delta, phi = phi,
        qx = qx, qy = qy,
        periodicX = periodicX, periodicY = periodicY,
        k = k, sigma = sigma, which = which, tol = tol, maxiter = maxiter
        )[int(k/2):][::2]
    #print(Ef)

    m = np.array((Ef - Ei)/(gammanew - gammax)) #slope, linear dependence on gamma
    #print(m)
    b = np.array(Ei - m*gammax) #y-intercept
    G_crit = np.array(-b/m) #gamma value that E=0 for given mu value
    #print(G_crit)
    return G_crit

"""
This function calculates the topological phase transition points.

To work it needs to calculate energy eigenvalues and eigenvectors of unperturbed Hamiltonian, or a Hamiltonian without any Zeeman field.

When a Zeeman field is turned on, a perturbed Hamiltonian can be used to calculate the new energy eigenvalues and eigenvectors from a reduced subspace of the initial Hilbert space.

This function also assumes that the phase transition points occur at kx=0
This will need to be reproduced to find energy minima in phase space for topological gap size

To have any meaning behind a phase boundary, the system must be perioidic and thus requires a neighbor boundary array. again, qx is assumed to be zero
"""
def local_min_gam_finder(
    coor, NN, NNb, ax, ay, mu, gi, gf,
    Wj = 0, cutx = 0, cuty = 0,
    Vj = 0, Vsc = 0, meff_normal = 0.026*const.m0, meff_sc = 0.026*const.m0,
    g_normal = 26, g_sc = 26,
    alpha = 0, delta = 0, phi = 0,
    Tesla = False, diff_g_factors = True,  Rfactor = 0, diff_alphas = False, diff_meff = False,
    k = 50, tol = 0.001
    ):
    Lx = (max(coor[:, 0]) - min(coor[:, 0]) + 1)*ax #Unit cell size in x-direction

    #gamz and qx are finite in order to avoid degneracy issues
    H0 = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, Vj=Vj, Vsc=Vsc, mu=mu, gamx=1e-4, alpha=alpha, delta=delta, phi=phi, qx=0, Tesla=Tesla, diff_g_factors=diff_g_factors, Rfactor=Rfactor, diff_alphas=diff_alphas, diff_meff=diff_meff) #gives low energy basis

    eigs_0, vecs_0 = spLA.eigsh(H0, k=k, sigma=0, which='LM')
    vecs_0_hc = np.conjugate(np.transpose(vecs_0)) #hermitian conjugate

    H_G1 = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, Vj=Vj, Vsc=Vsc, mu=mu, gamx=1+1e-4, alpha=alpha, delta=delta, phi=phi, qx=0, Tesla=Tesla, diff_g_factors=diff_g_factors, Rfactor=Rfactor, diff_alphas=diff_alphas, diff_meff=diff_meff) #Hamiltonian with ones on Zeeman energy along x-direction sites

    HG = H_G1 - H0 #the proporitonality matrix for gam-x, it is ones along the sites that have a gam value

    HG0_DB = np.dot(vecs_0_hc, H0.dot(vecs_0))
    HG_DB = np.dot(vecs_0_hc, HG.dot(vecs_0))

    G_crit = []
    delta_gam = abs(gf - gi)
    steps = int((delta_gam/(0.5*tol))) + 1
    gx = np.linspace(gi, gf, steps)
    eig_arr = np.zeros((gx.shape[0]))
    for i in range(gx.shape[0]):
        H_DB = HG0_DB + gx[i]*HG_DB
        eigs_DB, U_DB = LA.eigh(H_DB)
        eig_arr[i] = eigs_DB[int(k/2)]

    #checking edge cases
    if eig_arr[0] < tol:
        G_crit.append(gx[0])
    if eig_arr[-1] < tol:
        G_crit.append(gx[-1])

    local_min_idx = np.array(argrelextrema(eig_arr, np.less)[0]) #local minima indices in the E vs gam plot
    print(local_min_idx.size, "Energy local minima found at gx = ", gx[local_min_idx])
    #plt.plot(gx, eig_arr, c='b')
    #plt.scatter(gx[local_min_idx], eig_arr[local_min_idx], c='r', marker = 'X')
    #plt.show()

    tol = tol/10
    for i in range(0, local_min_idx.size): #eigs_min.size
        gx_c = gx[local_min_idx[i]] #gx[ZEC_idx[i]]""" #first approx g_critical
        gx_lower = gx[local_min_idx[i]-1]#gx[ZEC_idx[i]-1]""" #one step back
        gx_higher = gx[local_min_idx[i]+1]#gx[ZEC_idx[i]+1]""" #one step forward

        delta_gam = (gx_higher - gx_lower)
        n_steps = (int((delta_gam/(0.5*tol))) + 1)
        gx_finer = np.linspace(gx_lower, gx_higher, n_steps) #high res gam around supposed zero energy crossing (local min)
        eig_arr_finer = np.zeros((gx_finer.size)) #new eigenvalue array
        for j in range(gx_finer.shape[0]):
            H_DB = HG0_DB + gx_finer[j]*HG_DB
            eigs_DB, U_DB = LA.eigh(H_DB)
            eig_arr_finer[j] = eigs_DB[int(k/2)] #k/2 -> lowest postive energy state

        min_idx_finer = np.array(argrelextrema(eig_arr_finer, np.less)[0]) #new local minima indices
        eigs_min_finer = eig_arr_finer[min_idx_finer] #isolating local minima
        #plt.plot(gx_finer, eig_arr_finer, c = 'b')
        #plt.scatter(gx_finer[min_idx_finer], eig_arr_finer[min_idx_finer], c='r', marker = 'X')
        #plt.plot(gx_finer, 0*gx_finer, c='k', lw=1)
        for m in range(eigs_min_finer.shape[0]):
            if eigs_min_finer[m] < tol:
                crossing_gam = gx_finer[min_idx_finer[m]]
                G_crit.append(crossing_gam)
                print("Crossing found at Gx = {} | E = {} meV".format(crossing_gam, eigs_min_finer[m]))
                #plt.scatter(G_crit, eigs_min_finer[m], c= 'r', marker = 'X')
            #plt.show()
    G_crit = np.array(G_crit)
    return G_crit

def SNRG_gam_finder(
    ax, ay, mu, gi, gf,
    Wj = 0, Lx = 0, cutx = 0, cuty = 0,
    Vj = 0, Vsc = 0,  m_eff = 0.026,
    alpha = 0, delta = 0, phi = 0,
    k = 20, tol = 5e-6
    ):
    delta_gam = abs(gf-gi)
    n1, n2 = step_finder(delta_gam/(0.5*tol) + 1, 2)

    H0 = SNRG.Junc_eff_Ham_gen(omega=0, Wj=Wj, Lx=Lx, nodx=cutx, nody=cuty, ax=ax, ay=ay, kx=0, m_eff=m_eff, alp_l=alpha, alp_t=alpha, mu=mu, Vj=Vj, Vsc=Vsc, Gam=1e-7, delta=delta, phi=phi)
    eigs, vecs = spLA.eigsh(H0, k=k, sigma=0, which='LM')
    vecs_hc = np.conjugate(np.transpose(vecs)) #hermitian conjugate
    idx_sort = np.argsort(eigs)
    eigs = eigs[idx_sort]
    #print(eigs)

    H_G1 = SNRG.Junc_eff_Ham_gen(omega=0, Wj=Wj, Lx=Lx, nodx=cutx, nody=cuty, ax=ax, ay=ay, kx=0, m_eff=m_eff, alp_l=alpha, alp_t=alpha, mu=mu, Vj=Vj, Vsc=Vsc, Gam=1+1e-7, delta=delta, phi=phi) #Hamiltonian with ones on Zeeman energy along x-direction sites

    HG = H_G1 - H0 #the proporitonality matrix for gam-x, it is ones along the sites that have a gam value
    HG0_DB = np.dot(vecs_hc, H0.dot(vecs))
    HG_DB = np.dot(vecs_hc, HG.dot(vecs))

    G_crit = []
    delta_gam = abs(gf - gi)
    steps = n1
    gx = np.linspace(gi, gf, steps)
    eig_arr = np.zeros((4, gx.shape[0]))
    for i in range(gx.shape[0]):
        H_DB = HG0_DB + gx[i]*HG_DB
        eigs_DB, U_DB = LA.eigh(H_DB)
        idx_sort = np.argsort(eigs_DB)
        eigs_DB = eigs_DB[idx_sort]
        #eig_arr[i] = eigs_DB[int(k/2)]
        eig_arr[:,i] = eigs_DB[int(k/2)-2:int(k/2)+2]

    #checking edge cases
    if eig_arr[2,0] < tol:
        G_crit.append(gx[0])
    if eig_arr[2,-1] < tol:
        G_crit.append(gx[-1])

    local_min_idx = np.array(argrelextrema(eig_arr[2,:], np.less)[0])
    #for i in range(local_min_idx.shape[0]):
    #    print(eig_arr[:, local_min_idx[i]])
    #sys.exit()
    #local minima indices in the E vs gam plot
    print(local_min_idx.size, "Energy local minima found at gx = ", gx[local_min_idx])

    #for i in range(eig_arr.shape[0]):
    #    plt.plot(gx, eig_arr[2,:], c='b')
    #plt.plot(gx, eig_arr[2,:], c='r')
    #plt.scatter(gx[local_min_idx], eig_arr[2, local_min_idx], c='r', marker = 'X')
    #plt.show()

    for i in range(0, local_min_idx.size): #eigs_min.size
        gx_c = gx[local_min_idx[i]] #first approx g_critical
        gx_lower = gx[local_min_idx[i]-1]# one step back
        gx_higher = gx[local_min_idx[i]+1]#one step forward

        delta_gam = (gx_higher - gx_lower)
        n_steps = n2
        gx_finer = np.linspace(gx_lower, gx_higher, n_steps)
        eig_arr_finer = np.zeros((gx_finer.size))
        for j in range(gx_finer.shape[0]):
            H_DB = HG0_DB + gx_finer[j]*HG_DB
            eigs_DB, U_DB = LA.eigh(H_DB)
            idx_sort = np.argsort(eigs_DB)
            eigs_DB = eigs_DB[idx_sort]
            eig_arr_finer[j] = eigs_DB[int(k/2)]

        min_idx_finer = np.array(argrelextrema(eig_arr_finer, np.less)[0]) #new local minima indices
        #min_idx_finer = np.concatenate((np.array([0, n2-1]), min_idx_finer), axis=None)
        eigs_min_finer = eig_arr_finer[min_idx_finer] #isolating local minima

        #plt.plot(gx_finer, eig_arr_finer, c = 'b')
        #plt.scatter(gx_finer[min_idx_finer], eig_arr_finer[min_idx_finer], c='r', marker = 'X')
        #plt.plot(gx_finer, 0*gx_finer, c='k', lw=1)
        #plt.show()

        for m in range(eigs_min_finer.shape[0]):
            if abs(eigs_min_finer[m]) < tol:
                crossing_gam = gx_finer[min_idx_finer[m]]
                G_crit.append(crossing_gam)
                print("Crossing found at Gx = {} | E = {} meV".format(crossing_gam, eigs_min_finer[m]))

    G_crit = np.array(G_crit)
    return G_crit

def gap_finder(
    coor, NN, NNb, ax, ay, mu, gx,
    Wj = 0, cutx = 0, cuty = 0,
    Vj = 0, Vsc = 0, alpha = 0, delta = 0, phi = 0,
    meff_normal = 0.026*const.m0, meff_sc = 0.026*const.m0,
    g_normal = 26, g_sc = 26,
    Tesla = False, diff_g_factors = True,  Rfactor = 0, diff_alphas = False, diff_meff = False,
    k = 4, steps_targ = 1000
    ):

    n1, n2 = step_finder(steps_targ)
    print("total avg steps = ", n1+7*n2)
    Lx = (max(coor[:, 0]) - min(coor[:, 0]) + 1)*ax #Unit cell size in x-direction
    qx = np.linspace(0, np.pi/Lx, n1) #kx in the first Brillouin zone
    bands = np.zeros((n1, k))
    for i in range(n1):
        print(n1 - i)
        H = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, mu=mu, Vj=Vj, Vsc=Vsc, alpha=alpha, delta=delta, phi=phi, gamx=gx, qx=qx[i], Tesla=Tesla, diff_g_factors=diff_g_factors, diff_alphas=diff_alphas, diff_meff=diff_meff )
        eigs, vecs = spLA.eigsh(H, k=k, sigma=0, which='LM')
        idx_sort = np.argsort(eigs)
        eigs = eigs[idx_sort]
        bands[i, :] = eigs

    lowest_energy_band = bands[:, int(k/2)]
    local_min_idx = np.array(argrelextrema(lowest_energy_band, np.less)[0])
    print(local_min_idx.size, "Energy local minima found at kx = ", qx[local_min_idx])

    #for i in range(bands.shape[1]):
    #    plt.plot(qx, bands[:, i], c ='mediumblue', linestyle = 'solid')
    #plt.scatter(qx[local_min_idx], lowest_energy_band[local_min_idx], c='r', marker = 'X')
    #plt.show()

    min_energy = []
    qx_crit_arr = []
    #checking edge cases
    min_energy.append(bands[0, int(k/2)])
    qx_crit_arr.append(qx[0])
    min_energy.append(bands[-1, int(k/2)])
    qx_crit_arr.append(qx[-1])

    for i in range(local_min_idx.size): #eigs_min.size
        qx_c = qx[local_min_idx[i]] #first approx kx of band minimum
        qx_lower = qx[local_min_idx[i]-1] #one step back
        qx_higher = qx[local_min_idx[i]+1] #one step forward

        qx_finer = np.linspace(qx_lower, qx_higher, n2) #around local min
        bands_finer = np.zeros((n2, k)) #new eigenvalue array
        for j in range(n2):
            H = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, mu=mu, Vj=Vj, Vsc=Vsc, alpha=alpha, delta=delta, phi=phi, gamx=gx, qx=qx_finer[j], Tesla=Tesla, diff_g_factors=diff_g_factors, diff_alphas=diff_alphas, diff_meff=diff_meff )
            eigs, vecs = spLA.eigsh(H, k=k, sigma=0, which='LM')
            idx_sort = np.argsort(eigs)
            eigs = eigs[idx_sort]
            bands_finer[j, :] = eigs

        leb_finer = bands_finer[:, int(k/2)]
        min_idx_finer = np.array(argrelextrema(leb_finer, np.less)[0])
        leb_min_finer = leb_finer[min_idx_finer] #isolating local minima
        qx_crit = qx_finer[min_idx_finer]

        #for b in range(bands.shape[1]):
        #    plt.plot(qx_finer, bands_finer[:, b], c ='mediumblue', linestyle = 'solid')
        #plt.scatter(qx_finer[min_idx_finer], leb_min_finer, c='r', marker = 'X')
        #plt.show()

        leb_min_finer = np.array(leb_min_finer)
        GAP, IDX = minima(leb_min_finer)
        min_energy.append(GAP)
        qx_crit_arr.append(qx_crit[IDX])

    min_energy = np.array(min_energy)
    gap, idx = minima(min_energy)
    qx_crit = qx_crit_arr[idx]

    return gap, qx_crit
