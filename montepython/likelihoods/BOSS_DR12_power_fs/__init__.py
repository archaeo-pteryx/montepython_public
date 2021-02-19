from montepython.likelihood_class import Likelihood
import numpy as np
from mpi4py import MPI
import logging
import os, sys, time
import boss_dr12_power_fs_likelihood as utils

class BOSS_DR12_power_fs(Likelihood):
    def __init__(self, path, data, command_line):
        path = data.path['data']
        print('path:', path)
        Likelihood.__init__(self, path, data, command_line)

        print('loading data...')
        k = np.load(os.path.join(self.data_directory, self.k_file))
        signal = np.load(os.path.join(self.data_directory, self.signal_file))
        cov = np.load(os.path.join(self.data_directory, self.cov_file))
        self.config = utils.load_config(self.config_file)

        z_list = np.loadtxt(os.path.join(self.data_directory, 'redshift_'+self.config['type']+'.dat'))
        z_idx = self.config['observables']['power_fs']['z_idx']
        self.config['observables']['power_fs']['redshift'] = z_list[z_idx]
        self.config['window_datadir'] = os.path.join(self.data_directory,self.window_directory)

        k_list, data_list, cov_list = utils.load_data(k,signal,cov,self.config)
        data_vec, cov_mat, invcov_mat, f_Hartlap = utils.create_combined_data(data_list, cov_list, Hartlap=True, Nr=2048)

        model_name = self.config['observables']['power_fs']['model']['class']
        self.like = utils.likelihood(k_list, data_vec, invcov_mat * f_Hartlap, self.config, model_name, 'boss_dr12_power_fs_likelihood')

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        dirname_log = os.path.join(command_line.folder,'log_boss_dr12_power_fs')
        print('Initialize rank = %s' % rank)
        if rank == 0:
            if not os.path.exists(dirname_log): os.makedirs(dirname_log)
        logging.basicConfig(filename=os.path.join(dirname_log, 'log_%s' % rank), level=logging.INFO)

    def loglkl(self, cosmo, data):
        # We do not use 'cosmo', since we use the emulator to compute cosmological quantities.
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        print('Computing the log-likelihood at rank = %s' % rank)

        params = self.config['parameters'].copy()
        theta = []
        for name in params:
            if not params[name]['sampled']: continue
            params[name]['value'] = data.mcmc_parameters[name]['current']
            theta.append(params[name]['value'])
        theta = np.array(theta)
        logging.info('theta = %s' % theta)

        ti = time.time()
        lnprob, deriv_params = self.like.get_lnprob(params)
        tf = time.time()

        if deriv_params != None:
            for name in deriv_params.keys():
                data.mcmc_parameters[name]['current'] = deriv_params[name]

        print('done. The elapsed time at rank = %s: %s sec' % (rank, (tf-ti)))
        return lnprob
