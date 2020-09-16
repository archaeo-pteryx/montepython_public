from montepython.likelihood_class import Likelihood
import numpy as np
import xarray as xr
from mpi4py import MPI
import logging
import os, sys, time
sys.path.append('/work/yosuke.kobayashi/mcmc')
# sys.path.append('/raid/kobayashi/mcmc')
import boss_dr12_power_fs_likelihood as utils

class BOSS_DR12_power_fs(Likelihood):
    def __init__(self, path, data, command_line):
        print('path:', path)
        Likelihood.__init__(self, path, data, command_line)

        k = np.load(os.path.join(self.data_directory, self.k_file))
        signal = np.load(os.path.join(self.data_directory, self.signal_file))
        cov = np.load(os.path.join(self.data_directory, self.cov_file))
        self.config = utils.load_config(self.config_file)
        self.config['window_datadir'] = os.path.join(self.data_directory,self.window_directory)
        k,data_vec,cov_mat = utils.load_data(k,signal,cov,self.config)
        self.like = utils.likelihood(k,data_vec,cov_mat,self.config,self.config['parameter_values'])
        self.like.calc_invcov(Nr=2048)

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        dirname_log = os.path.join(command_line.folder,'log_boss_dr12_power_fs')
        print('initialize rank=%s' % rank)
        if rank == 0:
            if not os.path.exists(dirname_log):
                os.makedirs(dirname_log)
        logging.basicConfig(filename=os.path.join(dirname_log, 'log_' + '.%s' % rank), level=logging.INFO)

    def loglkl(self, cosmo, data):
        # We do not use 'cosmo', since we use the emulator to compute cosmologial quantities.
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        print('compute loglkl at rank=%s' % rank)

        theta = []
        for param in self.config['parameters']:
            if not param['do_sample']: continue
            if param['nspecies'] == 1: theta.append(data.mcmc_parameters[param['name']]['current'])
            else: # for e.g., HOD parameters.
                for i in range(param['nspecies']):
                    theta.append(data.mcmc_parameters[param['name']+'_%s' % i]['current'])
        theta = np.array(theta)
        logging.info('theta = %s' % theta)

        ti = time.time()
        lnprob, sigma8 = self.like.get_lnprob(theta)
        tf = time.time()

        data.mcmc_parameters['Omega_m']['current'] = 1.-data.mcmc_parameters['Omega_de']['current']
        data.mcmc_parameters['sigma_8']['current'] = sigma8

        print('elapsed time to compute loglkl at rank=%s: %s sec' % (rank, (tf-ti)))
        return lnprob
