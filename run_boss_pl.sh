#!/bin/bash
#PBS -q mini
#PBS -l nodes=1:ppn=4
#PBS -l walltime=7:04:00:00
#PBS -l mem=40GB
#PBS -m n
#PBS -V
#PBS -e mpiout/boss_dr12.err
#PBS -o mpiout/boss_dr12.out
#PBS -N mcmc

workdir='/work/yosuke.kobayashi/mcmc/montepython_public/'
cd ${workdir}

### # of cores for parallel computing that should be same as 'ppn' value
npro=4

### Multinest parameters
ISflag=True
efr=0.8
tol=0.5
nlive=1000
niter=100000
seed=1
####

### input parameter file
paramfile=input/BOSS_DR12_power_fs.param

### output directory
out_chains=chains/BOSS_DR12_power_fs
if [ ! -d $out_chains ]; then
	mkdir $out_chains
fi

# module load mpi/mpich-x86_64

mpirun -np ${npro} python ./montepython/MontePython.py run -p ${paramfile} -o ${out_chains} -N 50000 > log_boss_dr12.txt
