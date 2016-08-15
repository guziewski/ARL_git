import math
import os

#Topaz (36 processors/core)
def write_submit_topaz(fname,jobname,procnum,walltime,qtype,directory,input,output):
    cores=int(math.ceil(procnum/36.0))
    f = open(fname,'w')
    f.write('#!/bin/bash \n')
    f.write('#PBS -A ARLAP38753387 \n')
    f.write('#PBS -q '+qtype+' \n')
    f.write('#PBS -l select='+repr(cores)+':ncpus=36:mpiprocs=36 \n')
    f.write('#PBS -l walltime='+walltime+' \n')
    f.write('#PBS -l application=LAMMPS \n')
    f.write('#PBS -j oe \n')
    f.write('#PBS -N '+jobname+' \n\n')
    f.write('cd '+directory+' \n\n')
    f.write('mpiexec_mpt -np '+repr(procnum)+' ~/LAMMPS/src/lmp_topaz < '+input+' > '+output)
    f.close();

    return

def write_submit_copper(fname,jobname,procnum,walltime,qtype,directory,input,output):
    cores=int(math.ceil(procnum/32.0))
    f = open(fname,'w')
    f.write('#!/bin/bash \n')
    f.write('#PBS -A ARLAP38753875 \n')
    f.write('#PBS -q '+qtype+' \n')
    f.write('#PBS -l select='+repr(cores)+':ncpus=36:mpiprocs=36 \n')
    f.write('#PBS -l walltime='+walltime+' \n')
    f.write('#PBS -l application=LAMMPS \n')
    f.write('#PBS -j oe \n')
    f.write('#PBS -N '+jobname+' \n\n')
    f.write('cd '+directory+' \n\n')
    f.write('aprun -n '+repr(procnum)+' ~/Lammps/src/lmp_copper < '+input+' > '+output)
    f.close();
                    
                    
    return


def write_submit_excalibur(fname,jobname,procnum,walltime,qtype,directory,input,output):
    cores=int(math.ceil(procnum/32.0))
    f = open(fname,'w')
    f.write('#!/bin/bash \n')
    f.write('#PBS -A ARLAP38753875 \n')
    f.write('#PBS -q '+qtype+' \n')
    f.write('#PBS -l select='+repr(cores)+':ncpus=36:mpiprocs=36 \n')
    f.write('#PBS -l place=scatter:excl \n')
    f.write('#PBS -l walltime='+walltime+' \n')
    f.write('#PBS -l application=LAMMPS \n')
    f.write('#PBS -j oe \n')
    f.write('#PBS -N '+jobname+' \n\n')
    f.write('cd '+directory+' \n\n')
    f.write('aprun -n '+repr(procnum)+' ~/lammps-/src/lmp_excalibur < '+input+' > '+output)
    f.close();


    return

