#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import matplotlib.pyplot as plt
from numpy import linalg as LA
import matplotlib.lines as mlines
from scipy import interpolate

import lattice as lat
import constants as const
import operators as op


# In[3]:


ax = .1  #unit cell size along x-direction in [A]
ay = .1
Ny = 25    #number of lattice sites in y direction
Nx = 25     #number of lattice sites in x direction
N = Ny*Nx


# In[4]:


xbase = 40
xcut = 5
y1 = 10
y2 = 10


# In[5]:


CA = lat.Ibeam(xbase, xcut, y1, y2)
NN = lat.NN_Arr(CA)
energy, states = op.diagH(CA, ax, ay)


# In[6]:


get_ipython().run_line_magic('matplotlib', 'notebook')
plt.scatter(CA[:,0], CA[:,1])
plt.show()


# In[7]:


get_ipython().run_line_magic('matplotlib', 'notebook')
#This is to visualize the array as points and see if the nearest neighbor array is working correctly
idx = 44
plt.scatter(CA[:,0],CA[:,1],c = 'b')
plt.scatter(CA[idx,0],CA[idx,1],c = 'r')
plt.scatter(CA[NN[idx,0],0], CA[NN[idx,0],1],c = 'g')
plt.scatter(CA[NN[idx,1],0], CA[NN[idx,1],1],c = 'magenta')
plt.scatter(CA[NN[idx,2],0], CA[NN[idx,2],1],c = 'purple')
plt.scatter(CA[NN[idx,3],0], CA[NN[idx,3],1],c = 'cyan')
plt.show()


# In[8]:


#Ibeam Eigenvalues
print(energy.shape)
print(energy[0:10]/energy[0])


# In[9]:


get_ipython().run_line_magic('matplotlib', 'notebook')
op.state_cplot(CA, states[:, 100])    


# In[ ]:



