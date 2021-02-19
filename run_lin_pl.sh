#!/bin/bash
#PBS -q mini2
#PBS -l nodes=1:ppn=8
#PBS -l walltime=7:04:00:00
#PBS -l mem=40GB
#PBS -m n
#PBS -V
#PBS -N run_mn

workdir=/work/yosuke.kobayashi/mcmc/montepython_public/
cd ${workdir}

### # of cores for parallel computing that should be same as 'ppn' value
npro=8

### Multinest parameters
ISflag=True
efr=0.8
tol=0.5
nlive=1000
niter=10000
seed=1
####

### input parameter file
paramfile=input/linear_power_fs.param

### output directory
out_chains=chains/linear_power_fs/run_hod_p02_z0_efr${efr}_tol${tol}_s${seed}
if [ ! -d $out_chains ]; then
	mkdir $out_chains
fi

# module load mpi/mpich-x86_64

mpirun -np ${npro} python ./montepython/MontePython.py run -p ${paramfile} -o ${out_chains} -m NS --NS_importance_nested_sampling ${ISflag} --NS_evidence_tolerance ${efr} --NS_sampling_efficiency ${tol} --NS_n_live_points ${nlive} --NS_max_iter ${niter} --NS_seed ${seed} \
1> ${out_chains}/out.log 2> ${out_chains}/err.log
