import numpy
import math
import os




#Crystalography
material='Ni'
crystaltype='fcc'       #bcc, fcc, or hcp
a=2.86                  #Lattice constant approximation
c=1.624*a                     #only matters if hcp

unitcell_dump=''           #Only if not bcc, fcc, or hcp
unit_timestep=0


#Potential
pair_style='eam/fs'
pair_coeff='* * Potentials/ATVF.eam.fs Ni'
mass=55.85

os.system('mkdir ThermalData')
os.system('mkdir ThermalData/'+material+'_'+crystaltype)

#Calculate temperature dependent lattice constants
#Create LAMMPS input script ramping up temperature
f = open('ThermalData/'+material+'_'+crystaltype+'/temp_'+material+'.in','w')
f.write('#LAMMPS input file to calculate temperature dependent lattice constants of '+material+' \n')
f.write('dimension 3 \n')
f.write('boundary p p p \n')
f.write('units metal \n')
f.write('atom_style atomic \n')
if crystaltype=='fcc' or crystaltype=='bcc' or crystaltype=='hcp':
    f.write('lattice '+crystaltype+' '+repr(a)+' origin .01 .01 .01 \n')
    f.write('region box block 0 8 0 8 0 8 units lattice \n')
    f.write('create_box 1 box \n')
    f.write('create_atoms 1 box \n')
else:
    f.write('lattice bcc '+repr(a)+' origin .01 .01 .01 \n')
    f.write('region box block 0 8 0 8 0 8 units lattice \n')
    f.write('create_box 1 box \n')
    f.write('read_dump '+unitcell_dump+' '+repr(unit_timestep)+' box yes replace yes \n')
    f.write('replicate 8 8 8 \n')
    f.write('reset_timestep 0 \n')
f.write('pair_style '+pair_style+'\n')
f.write('pair_coeff '+pair_coeff+'\n')
f.write('mass 1 '+repr(mass)+' \n')
f.write('variable Lx equal lx/8 \n')
f.write('variable Ly equal ly/8 \n')
f.write('variable Lz equal lz/8 \n')
f.write('variable T equal temp \n')
f.write('thermo 1000 \n')
f.write('thermo_style custom step temp etotal press \n')
f.write('fix zeroK all box/relax x 0.0 y 0.0 z 0.0 \n')
f.write('minimize 1e-12 1e-12  100000 100000 \n')
f.write('fix 2 all print 1 "${T} ${Lx} ${Ly} ${Lz}" file ThermalData/'+material+'_'+crystaltype+'/LatticeConst title "Temperature dependent lattice constants (T a b c)" \n')
f.write('run 1 \n')
f.write('reset_timestep 0 \n')
f.write('unfix zeroK \n')
f.write('unfix 2 \n')
f.write('timestep 0.001 \n')
f.write('velocity all create 5 1 \n')
for j in range(0,20):
    X=int(j*50)
    Y=int((j+1)*50)
    if j==0:
        f.write('fix integrator all npt iso 0 0 1 temp 1 '+repr(Y)+' .1 \n')
    else:
        f.write('fix integrator all npt iso 0 0 1 temp '+repr(X)+' '+repr(Y)+' .1 \n')
    f.write('run 10000 \n')
    f.write('unfix integrator \n')
    f.write('fix integrator all npt iso 0 0 1 temp '+repr(Y)+' '+repr(Y)+' .1 \n')
    f.write('fix 3 all print 1 "${T} ${Lx} ${Ly} ${Lz}" file ThermalData/'+material+'_'+crystaltype+'/Temp'+repr(Y)+'.out title "" screen no \n')
    f.write('run 5000 \n')
    f.write('unfix 3 \n')
    f.write('unfix integrator \n')
f.close()

os.system('mpiexec -np 2 ~/Desktop/lmp_mpi <ThermalData/'+material+'_'+crystaltype+'/temp_'+material+'.in> ThermalData/'+material+'_'+crystaltype+'/Temp.out')


#Average out data from constant temperature holds
for j in range(0,20):
    Y=int((j+1)*50)
    f = open('ThermalData/'+material+'_'+crystaltype+'/Temp'+repr(Y)+'.out','r')
    f.readline()
    T=0; Lx=0; Ly=0; Lz=0;
    for k in range(0,5000):
        line=f.readline()
        data=line.split(' ')
        T=T+float(data[0]); Lx=Lx+float(data[1]); Ly=Ly+float(data[2]); Lz=Lz+float(data[3]);
    os.system('rm ThermalData/'+material+'_'+crystaltype+'/Temp'+repr(Y)+'.out')
    T=T/5000; Lx=Lx/5000; Ly=Ly/5000; Lz=Lz/5000;
    g = open('ThermalData/'+material+'_'+crystaltype+'/LatticeConst','a')
    g.write(repr(T)+' '+repr(Lx)+' '+repr(Ly)+' '+repr(Lz)+'\n')
    g.close()
f.close()