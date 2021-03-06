import numpy
import math
import os
from submit_maker import *
import time

#NOTE: ThermalData.py for the given material and crystaltype must have previously been run


#Dump file from Shawn's GB (Output: id type x y z)
dumpfile='InitialDumpfiles/twist__Cu__0_0_1__37.99_deg_GBE_1109.dump'


#Temperatures to be analyzed
Temps=[42]

#Driving energies to be considered (+/- u0/2 added to each crystal for ECO, u0 added to one crystal for orient)
u0=[.025, .05, .075, .1, .125];

#Orientation Title
Orientation='Cu_twist_1109'

#Computational machine
machine='topaz'

#Parameters
rcut=2.75                  #ECO cutoff radius
eta=.25                    #ECO cutoff parmater (.25 in most cases)
cutlo=.4                   #orient cutoff parameters (between 0 and 1)
cuthi=.6
timesteps=300000



#Crystalography
material='Cu'
crystaltype='fcc'       #bcc, fcc, or hcp
a=3.615                  #Lattice constant approximation
c=1.624*a                     #only matters if hcp
ori1x=numpy.array([7, -3, 0]) #Orientation 1 will grow
ori1y=numpy.array([0, 0, 1])
ori1z=numpy.array([-3, -7, 0])
ori2x=numpy.array([-11, -20, 0])
ori2y=numpy.array([0, 0, 1])
ori2z=numpy.array([20, -11, 0])

unitcell_dump=''           #Only if not bcc, fcc, or hcp
unit_timestep=0


#Potential
pair_style='eam/alloy'
pair_coeff='* * Potentials/Cu01.eam.alloy'
mass=55.85

os.system('mkdir MobilityData')
os.system('mkdir MobilityData/'+material+'_'+crystaltype)
os.system('mkdir MobilityData/'+material+'_'+crystaltype+'/'+Orientation)
os.system('mkdir MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts')
os.system('mkdir MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps')
os.system('mkdir MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Outputfiles')
os.system('mkdir MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles')
#Create array of temperature dependent lattice constants
f = open('ThermalData/'+material+'_'+crystaltype+'/LatticeConst','r')
f.readline()
for i in range(0,21):
    line=f.readline()
    data=line.split(' ')
    if i == 0:
        TempData=numpy.array([float(data[0]),float(data[1]),float(data[3])])
    else:
        TempData=numpy.vstack([TempData,[float(data[0]),float(data[1]),float(data[3])]])
f.close()


#Find Particles on free surface
f = open(dumpfile,'r')
f.readline()
line2=f.readline()
data = line2.split(' ')
dump_timestep=int(data[0])
f.readline()
line4 = f.readline()
data=line4.split(' ')
N=int(data[0])
f.readline()
line6 = f.readline()
xdata=line6.split(' ')
Lx=float(xdata[1])-float(xdata[0])
line7 = f.readline()
ydata=line7.split(' ')
Ly=float(ydata[1])-float(ydata[0])
line8 = f.readline()
zdata=line8.split(' ')
Lz=float(zdata[1])-float(zdata[0])
f.readline()

#Use far side of box as starting points
ymin=float(ydata[1])
ymax=float(ydata[0])

#Find min and max values of particles in y-direction
for j in range(0,N):
    line = f.readline()
    data=line.split(' ')
    if float(data[3])<ymin:
        ymin=float(data[3])
    if float(data[3])>ymax:
        ymax=float(data[3])
f.close()

#Calculate regions for vy=0,fy=0 (Necessary to keep box stationary)
yhi=ymax-rcut
ylo=ymin+rcut

#Create Rotation Matrices
ori1x=ori1x/numpy.linalg.norm(ori1x)
ori1y=ori1y/numpy.linalg.norm(ori1y)
ori1z=ori1z/numpy.linalg.norm(ori1z)
ori2x=ori2x/numpy.linalg.norm(ori2x)
ori2y=ori2y/numpy.linalg.norm(ori2y)
ori2z=ori2z/numpy.linalg.norm(ori2z)

x=numpy.array([1,0,0])
y=numpy.array([0,1,0])
z=numpy.array([0,0,1])

R1=numpy.matrix([[float(numpy.dot(x,ori1x)),float(numpy.dot(y,ori1x)),float(numpy.dot(z,ori1x))],[float(numpy.dot(x,ori1y)),float(numpy.dot(y,ori1y)),float(numpy.dot(z,ori1y))],[float(numpy.dot(x,ori1z)),float(numpy.dot(y,ori1z)),float(numpy.dot(z,ori1z))]])
R2=numpy.matrix([[float(numpy.dot(x,ori2x)),float(numpy.dot(y,ori2x)),float(numpy.dot(z,ori2x))],[float(numpy.dot(x,ori2y)),float(numpy.dot(y,ori2y)),float(numpy.dot(z,ori2y))],[float(numpy.dot(x,ori2z)),float(numpy.dot(y,ori2z)),float(numpy.dot(z,ori2z))]])




#For temperatures to be analyzed, perform linear interpolation to find a and c
for j in range(0,len(Temps)):
    temp=Temps[j]
    for i in range(0,21):
        if temp<TempData[i][0]:
            T1=TempData[i-1][0]
            T2=TempData[i][0]
            a1=TempData[i-1][1]
            a2=TempData[i][1]
            c1=TempData[i-1][2]
            c2=TempData[i][2]
            break
    i=(temp-T1)/(T2-T1)
    a=(1-i)*a1+i*a2
    c=(1-i)*c1+i*c2


    #Define basis vectors
    if crystaltype=='fcc':
        a1=numpy.matrix([[a/2], [a/2],[0]])
        a2=numpy.matrix([[a/2], [0],[a/2]])
        a3=numpy.matrix([[0], [a/2],[a/2]])
    if crystaltype=='bcc':
        a1=numpy.matrix([[a/2], [a/2],[-a/2]])
        a2=numpy.matrix([[a/2], [-a/2],[a/2]])
        a3=numpy.matrix([[-a/2], [a/2],[a/2]])
    if crystaltype=='hcp':
        a1=numpy.matrix([[a], [0],[0]])
        a2=numpy.matrix([[-a/2], [a*math.sqrt(3)/2],[0]])
        a3=numpy.matrix([[a/2], [a*math.sqrt(3)/6],[c/2]])
    #Calculate Rotated Basis
    b1_1=R1*a1
    b2_1=R1*a2
    b3_1=R1*a3
    b1_2=R2*a1
    b2_2=R2*a2
    b3_2=R2*a3

    #Write Orientation file (ECO)
    f=open('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/eco_'+repr(temp)+'K.ori','w')
    f.write(str(b1_1[0]).strip('[]')+' '+str(b1_1[1]).strip('[]')+' '+str(b1_1[2]).strip('[]')+'\n')
    f.write(str(b2_1[0]).strip('[]')+' '+str(b2_1[1]).strip('[]')+' '+str(b2_1[2]).strip('[]')+'\n')
    f.write(str(b3_1[0]).strip('[]')+' '+str(b3_1[1]).strip('[]')+' '+str(b3_1[2]).strip('[]')+'\n')
    f.write(str(b1_2[0]).strip('[]')+' '+str(b1_2[1]).strip('[]')+' '+str(b1_2[2]).strip('[]')+'\n')
    f.write(str(b2_2[0]).strip('[]')+' '+str(b2_2[1]).strip('[]')+' '+str(b2_2[2]).strip('[]')+'\n')
    f.write(str(b3_2[0]).strip('[]')+' '+str(b3_2[1]).strip('[]')+' '+str(b3_2[2]).strip('[]')+'\n')
    f.close()

    #Calculate necessary size of simulation
    if crystaltype=='bcc' or crystaltype=='fcc':
        x1=numpy.linalg.norm(ori1x)*a
        x2=numpy.linalg.norm(ori2x)*a
        z1=numpy.linalg.norm(ori1z)*a
        z2=numpy.linalg.norm(ori2z)*a
        if x1==x2:
            dx=10*x1
        else:
            dx=abs(x1*x2/(x1-x2))
        if z1==z2:
            dz=10*z1
        else:
            dz=abs(z1*z2/(z1-z2))
        repx=int(math.ceil(dx/Lx))
        repz=int(math.ceil(dz/Lz))
	if repx>10:
		repx=1
	if repz>10:
		repz=1


    cutoff=2*rcut



    #Write restart file at temperature to be analyzed
    f=open('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/temp_equil_'+repr(temp)+'.in','w')
    f.write('#Thermal Equilibration Input File \n')
    f.write('dimension 3 \n')
    f.write('boundary p p p \n')
    f.write('units metal \n')
    f.write('atom_style atomic \n')
    f.write('lattice bcc '+repr(a)+' origin .01 .01 .01 \n')
    f.write('region box block 0 1 0 1 0 1 units lattice \n')
    f.write('create_box 4 box \n')
    f.write('read_dump '+dumpfile+' '+repr(dump_timestep)+' x y z box yes add yes \n')
    f.write('replicate '+repr(repx)+' 1 '+repr(repz)+' \n')
    f.write('reset_timestep 0 \n')
    f.write('pair_style '+pair_style+'\n')
    f.write('pair_coeff '+pair_coeff+' '+material+' '+material+' '+material+' '+material+' \n')
    f.write('comm_modify cutoff '+repr(cutoff)+'\n')
    f.write('comm_style tiled \n')
    f.write('balance 0.9 rcb \n')
    f.write('timestep 0.001 \n')
    f.write('thermo 1000 \n')
    f.write('velocity all create 5 1 \n')
    f.write('fix integrator all npt iso 0 0 1 temp 1 '+repr(temp)+' .1 \n')
    f.write('thermo_style custom step temp etotal press \n')
    f.write('run 20000 \n')
    f.write('unfix integrator \n')
    f.write('fix integrator all npt iso 0 0 1 temp '+repr(temp)+' '+repr(temp)+' .1 \n')
    f.write('run 5000 \n')
    f.write('write_restart MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/'+repr(temp)+'K.restart \n')
    f.write('run 0')
    f.close()


    write_submit_topaz('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_restartmaker'+repr(temp)+'K.bash',material+'_'+repr(temp)+'K_restart',72,'00:59:00','debug','/p/work1/mcg84/DrivingForce/test','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/temp_equil_'+repr(temp)+'.in','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Outputfiles/temp_equil_'+repr(temp)+'.out')
    os.system('qsub MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_restartmaker'+repr(temp)+'K.bash')

    for k in range(0,len(u0)):
        u=u0[k]
        #Write ECO Input file
        f=open('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/eco_'+repr(temp)+'K_'+repr(u)+'eV.in','w')
        f.write('#ECO input '+repr(temp)+'K_'+repr(u)+'eV \n')
        f.write('read_restart MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/'+repr(temp)+'K.restart \n')
        f.write('reset_timestep 0 \n')
        f.write('pair_style '+pair_style+'\n')
    	f.write('pair_coeff '+pair_coeff+' '+material+' '+material+' '+material+' '+material+' \n')
	f.write('comm_modify cutoff '+repr(cutoff)+'\n')
    	f.write('thermo 100 \n')
	f.write('fix integrator all npt iso 0 0 1 temp '+repr(temp)+' '+repr(temp)+' .1 \n')
        f.write('region ends block INF INF '+repr(ylo)+' '+repr(yhi)+' INF INF units box side out \n')
        f.write('group end region ends \n')
        f.write('fix eco all eco/force '+repr(u)+' '+repr(eta)+' '+repr(rcut)+' MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/eco_'+repr(temp)+'K.ori \n')
        f.write('fix edges end setforce NULL 0.0 NULL \n')
        f.write('velocity end set NULL 0.0 NULL \n')
        f.write('comm_style tiled \n')
        f.write('balance 0.9 rcb \n')
        f.write('thermo_style custom step temp etotal press f_eco \n')
        f.write('dump save all custom 1000 MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/eco_'+repr(temp)+'K_'+repr(u)+'eV.* id x y z f_eco[1] f_eco[2] f_eco[3] f_eco[4] f_eco[5] fx fy fz vx vy vz \n')
        f.write('dump_modify save sort id \n')
        f.write('run '+repr(timesteps))
        f.close()
        write_submit_topaz('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_'+repr(temp)+'K_'+repr(u)+'eV.bash',material+'_'+repr(temp)+'K_'+repr(u)+'eV',36,'08:00:00','standard','/p/work1/mcg84/DrivingForce/test','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/eco_'+repr(temp)+'K_'+repr(u)+'eV.in','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Outputfiles/'+repr(temp)+'K_'+repr(u)+'eV.out')

        while not os.path.exists('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/'+repr(temp)+'K.restart'):
            time.sleep(10)
            print('Waiting for restart file')
        os.system('qsub MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_'+repr(temp)+'K_'+repr(u)+'eV.bash')

#Define additional nearest neighbor vectors for orient/fcc(bcc) and write orientation files
	if crystaltype=='hcp':
    		quit()
	if crystaltype=='fcc':
    		a4=numpy.matrix([[-a/2], [a/2],[0]])
    		a5=numpy.matrix([[-a/2], [0],[a/2]])
    		a6=numpy.matrix([[0], [-a/2],[a/2]])
    		b4_1=R1*a4
    		b5_1=R1*a5
    		b6_1=R1*a6
    		b4_2=R2*a4
    		b5_2=R2*a5
    		b6_2=R2*a6
    		f=open('orient1.file','w')
    		f.write(str(b1_1[0]).strip('[]')+' '+str(b1_1[1]).strip('[]')+' '+str(b1_1[2]).strip('[]')+'\n')
    		f.write(str(b2_1[0]).strip('[]')+' '+str(b2_1[1]).strip('[]')+' '+str(b2_1[2]).strip('[]')+'\n')
    		f.write(str(b3_1[0]).strip('[]')+' '+str(b3_1[1]).strip('[]')+' '+str(b3_1[2]).strip('[]')+'\n')
    		f.write(str(b4_1[0]).strip('[]')+' '+str(b4_1[1]).strip('[]')+' '+str(b4_1[2]).strip('[]')+'\n')
    		f.write(str(b5_1[0]).strip('[]')+' '+str(b5_1[1]).strip('[]')+' '+str(b5_1[2]).strip('[]')+'\n')
    		f.write(str(b6_1[0]).strip('[]')+' '+str(b6_1[1]).strip('[]')+' '+str(b6_1[2]).strip('[]')+'\n')
    		f.close()
    		f=open('orient2.file','w')
    		f.write(str(b1_2[0]).strip('[]')+' '+str(b1_2[1]).strip('[]')+' '+str(b1_2[2]).strip('[]')+'\n')
    		f.write(str(b2_2[0]).strip('[]')+' '+str(b2_2[1]).strip('[]')+' '+str(b2_2[2]).strip('[]')+'\n')
    		f.write(str(b3_2[0]).strip('[]')+' '+str(b3_2[1]).strip('[]')+' '+str(b3_2[2]).strip('[]')+'\n')
    		f.write(str(b4_2[0]).strip('[]')+' '+str(b4_2[1]).strip('[]')+' '+str(b4_2[2]).strip('[]')+'\n')
    		f.write(str(b5_2[0]).strip('[]')+' '+str(b5_2[1]).strip('[]')+' '+str(b5_2[2]).strip('[]')+'\n')
    		f.write(str(b6_2[0]).strip('[]')+' '+str(b6_2[1]).strip('[]')+' '+str(b6_2[2]).strip('[]')+'\n')
    		f.close()
	if crystaltype=='bcc':
    		a4=numpy.matrix([[a/2], [a/2],[a/2]])
    		b4_1=R1*a4
    		b4_2=R2*a4
    		f=open('orient1.file','w')
    		f.write(str(b1_1[0]).strip('[]')+' '+str(b1_1[1]).strip('[]')+' '+str(b1_1[2]).strip('[]')+'\n')
    		f.write(str(b2_1[0]).strip('[]')+' '+str(b2_1[1]).strip('[]')+' '+str(b2_1[2]).strip('[]')+'\n')
    		f.write(str(b3_1[0]).strip('[]')+' '+str(b3_1[1]).strip('[]')+' '+str(b3_1[2]).strip('[]')+'\n')
    		f.write(str(b4_1[0]).strip('[]')+' '+str(b4_1[1]).strip('[]')+' '+str(b4_1[2]).strip('[]')+'\n')
    		f.close()
    		f=open('orient2.file','w')
    		f.write(str(b1_2[0]).strip('[]')+' '+str(b1_2[1]).strip('[]')+' '+str(b1_2[2]).strip('[]')+'\n')
    		f.write(str(b2_2[0]).strip('[]')+' '+str(b2_2[1]).strip('[]')+' '+str(b2_2[2]).strip('[]')+'\n')
    		f.write(str(b3_2[0]).strip('[]')+' '+str(b3_2[1]).strip('[]')+' '+str(b3_2[2]).strip('[]')+'\n')
    		f.write(str(b4_2[0]).strip('[]')+' '+str(b4_2[1]).strip('[]')+' '+str(b4_2[2]).strip('[]')+'\n')
    		f.close()

	#Write input file (orient)
	f=open('orient.in','w')
	f.write('#Orient Input File \n')
        f=open('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/orient_'+repr(temp)+'K_'+repr(u)+'eV.in','w')
        f.write('#Orient input '+repr(temp)+'K_'+repr(u)+'eV \n')
        f.write('read_restart MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/'+repr(temp)+'K.restart \n')
        f.write('reset_timestep 0 \n')
        f.write('pair_style '+pair_style+'\n')
        f.write('pair_coeff '+pair_coeff+' '+material+' '+material+' '+material+' \n')
        f.write('comm_modify cutoff '+repr(cutoff)+'\n')
        f.write('thermo 100 \n')
        f.write('fix integrator all npt iso 0 0 1 temp '+repr(temp)+' '+repr(temp)+' .1 \n')
        f.write('region ends block INF INF '+repr(ylo)+' '+repr(yhi)+' INF INF units box side out \n')
        f.write('group end region ends \n')
	f.write('fix orient all orient/'+crystaltype+' 0 1 '+repr(a)+' '+repr(u)+' '+repr(cutlo)+' '+repr(cuthi)+' orient1.file orient2.file \n')
	f.write('fix edges end setforce NULL 0.0 NULL \n')
        f.write('velocity end set NULL 0.0 NULL \n')
        f.write('comm_style tiled \n')
        f.write('balance 0.9 rcb \n')
        f.write('thermo_style custom step temp etotal press f_orient \n')
        f.write('dump save all custom 1000 MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Dumps/orient_'+repr(temp)+'K_'+repr(u)+'eV.* id x y z f_orient[1] f_orient[2] fx fy fz vx vy vz \n')
        f.write('dump_modify save sort id \n')
        f.write('run '+repr(timesteps))
        f.close()

	write_submit_topaz('MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_orient_'+repr(temp)+'K_'+repr(u)+'eV.bash',material+'_orient_'+repr(temp)+'K_'+repr(u)+'eV',36,'08:00:00','standard','~/DrivingForce/test','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/InputScripts/orient_'+repr(temp)+'K_'+repr(u)+'eV.in','MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Outputfiles/'+repr(temp)+'K_'+repr(u)+'eV_orient.out')
	#os.system('qsub MobilityData/'+material+'_'+crystaltype+'/'+Orientation+'/Submitfiles/submit_topaz_orient_'+repr(temp)+'K_'+repr(u)+'eV.bash')

