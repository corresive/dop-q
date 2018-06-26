#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================
***         Docker Priority Queue (DoP-Q)          ***
======================================================

    |Purpose: Priority queue to run docker containers

Created on Mon May 29 23:21:42 2017

History:
    16.10.2017: Changed to python 2.7

@author: markus
"""

from __future__ import print_function
import os
import numpy as np
import time
import docker
# import configparser # python 3
import ConfigParser  # python 2
import provider
import gpu_handler as gh
from pathos.helpers import mp
import dill
# import multiprocessing as mp  # cannot pass our container objects through the queue
# import pickle as pkl          # cannot pickle our container object, which causes the failure of the mp.Queue
import json
from utils import log


class DopQ(object):

    def __init__(self, configfile, logfile, debug=False):

        # get settings from config
        if not os.path.isfile(configfile):
            self.write_default_config(configfile)

        # init member variables
        self.client = docker.from_env()
        self.debug = debug
        self.configfile = configfile
        self.logfile = logfile
        self.config = self.parse_config(configfile)
        self.paths = self.config['paths']
        self.history_file = 'history.dill'
        self.container_list_file = 'container_list.dill'
        self.running_containers_file = 'running_containers.dill'
        self.container_list = []
        self.running_containers = []
        self.history = []
        self.mapping = {'history': (self.history_file, self.history),
                        'list': (self.container_list_file, self.container_list),
                        'running': (self.running_containers_file, self.running_containers)}
        self.restore('all')

        # init helper processes and classes
        self.queue = mp.Queue()
        self.gpu_handler = gh.GPUHandler()
        self.provider = provider.Provider(self.config, self.queue)

        # init logging
        self.logger = log.init_log()
        self.logger.info(time.ctime() + '\tinitializing dop-q' +
                         '\n\t\tpassed config:' + '\n\t\t' + json.dumps(self.config, indent=4))

        # make sure gpus can be assigned to containers
        assert (self.config['queue']['max_gpus'] > 0)

        # build all non-existent directories, except the network container share
        keys = self.paths.keys()
        for key in keys:
            if key != 'network_containers':
                if not os.path.isdir(self.paths[key]):
                    os.makedirs(self.paths[key])

    def restore(self, key):
        """
        restores history, container_list, running_containers, or all three
        :param key: dictionary key of self.mapping or 'all'
        :return: None
        """

        def restore_single(path, file, member):
            """
            helper for loading a single queue list
            :param path: directory of the dill file
            :param file: name of the dill file
            :param member: member that will be assigned the list
            :return: None
            """
            filename = os.path.join(path, file)
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    member = dill.load(f)
            else:
                member = []

        if key == 'all':
            for item in self.mapping.values():
                restore_single(self.paths['history'], *item)
        else:
            restore_single(self.paths['history'], *self.mapping[key])
            if key == 'running':
                self.update_running_containers()

    def save(self, key):
        """
        restores history, container_list, running_containers, or all three
        :param key: dictionary key of self.mapping or 'all'
        :return: None
        """

        def save_single(path, file, member):
            """
            helper for saving a single queue list
            :param path: directory of the dill file
            :param file: name of the dill file
            :param member: member that will be assigned the list
            :return: None
            """
            filename = os.path.join(path, file)
            with open(filename, 'wb') as f:
                dill.dump(member, f)

        if key == 'all':
            for item in self.mapping.values():
                save_single(self.paths['history'], *item)
        else:
            if key == 'running':
                self.update_running_containers()
            save_single(self.paths['history'], *self.mapping[key])

    def update_container_list(self):
        update_list = []

        # add new images that are obtained from the builder process
        while not self.queue.empty():
            update_list.append(self.queue.get())
        self.container_list += update_list

        # sort priority queue:
        self.container_list = sorted(self.container_list, key=self.sort_fn)

    def update_running_containers(self):
        running_containers = self.client.containers.list()
        for i, container in enumerate(self.running_containers):
            if container not in running_containers:
                self.running_containers.pop(i)

    def get_user_oh(self, user_name):
        user_oh = [int(el == user_name.lower()) for el in self.history]
        return np.array(user_oh)

    def calc_exp_decay(self):
        decay = [np.exp(-i) for i in range(len(self.history))]
        return np.array(decay)

    def calc_penalty(self, user_name):
        user_oh = self.get_user_oh(user_name)
        return np.sum(user_oh * self.calc_exp_decay())

    def get_user(self, container):
        return container.user

    def split_and_calc_penalty(self, container):
        user = self.get_user(container)
        return self.calc_penalty(user)

    def sort_fn(self, container):
        """
        function that is used for sorting the container list
        :param container: container object from the list
        :return: tuple consisting of user penalty and creation time of the container
        """
        return self.split_and_calc_penalty(container), container.created_at

    def show_penalties(self, docker_users):
        for user in docker_users:
            print("Penalty for {}: {}".format(user, round(self.calc_penalty(user), 4)))

    def sleep(self):
        time.sleep(self.config['queue']['sleep'])

    @staticmethod
    def write_default_config(configfile):
        """
        Write default configuration
        :return: None
        """

        config = ConfigParser.ConfigParser()

        config.add_section('paths')
        config.set('paths', 'container.dir', '/media/local/input_container/reception/')
        config.set('paths', 'network.dir', '/media/temporary_network_share/')
        config.set('paths', 'unzip.dir', '/media/local/input_container/unzipped/')
        config.set('paths', 'log.dir', '/media/local/output_container/logging/')
        config.set('paths', 'history.dir', './')
        config.set('paths', 'failed.dir', '/media/local/output_container/failed/')

        config.add_section('queue')
        config.set('queue', 'max.history', '100')
        config.set('queue', 'verbose', 'yes')
        config.set('queue', 'sleep.interval', '60')
        config.set('queue', 'max.gpu.assignment', '1')

        config.add_section('docker')
        config.set('docker', 'mount.volumes', '/media/data/expImages:/imgdir,/media/local/output_container:/outdir')
        config.set('docker', 'remove', 'yes')
        config.set('docker', 'network.mode', 'host')
        config.set('docker', 'mem.limit', '32g')
        config.set('docker', 'logging.interval', '10')

        config.add_section('fetcher')
        config.set('fetcher', 'valid.executors', 'anees,ilja,ferry,markus')
        config.set('fetcher', 'min.space', '0.05')
        config.set('fetcher', 'remove.invalid.containers', 'yes')
        config.set('fetcher', 'sleep.interval', '60')

        config.add_section('builder')
        config.set('builder', 'sleep.interval', '60')
        config.set('builder', 'load.suffix', 'tar')
        config.set('builder', 'build.suffix', 'zip')

        # store config
        with open(configfile, 'w') as conf:
            config.write(conf)

    @staticmethod
    def parse_config(configfile):

        # create config parser and read file
        config = ConfigParser.ConfigParser()
        config.read(configfile)

        # parse settings into dicts
        parsed_config = {
            'paths': {'local_containers': config.get('paths', 'container.dir'),
                      'network_containers': config.get('paths', 'network.dir'),
                      'unzip': config.get('paths', 'unzip.dir'),
                      'log': config.get('paths', 'log.dir'),
                      'history': config.get('paths', 'history.dir'),
                      'failed': config.get('paths', 'failed.dir')},

            'docker': {'mounts': config.get('docker', 'mount.volumes').split(','),
                       'auto_remove': config.getboolean('docker', 'remove'),
                       'mem_limit': config.get('docker', 'mem.limit'),
                       'network_mode': config.get('docker', 'network.mode'),
                       'logging_interval': config.getint('docker', 'logging.interval')},

            'queue': {'max_history': config.getint('queue', 'max.history'),
                      'verbose': config.getboolean('queue', 'verbose'),
                      'sleep': config.getint('queue', 'sleep.interval'),
                      'max_gpus': config.getint('queue', 'max.gpu.assignment')},

            'builder': {'sleep': config.getint('builder', 'sleep.interval'),
                        'load': config.get('builder', 'load.suffix').split(','),
                        'build': config.get('builder', 'build.suffix').split(',')},

            'fetcher': {'remove_invalid': config.getboolean('fetcher', 'remove.invalid.containers'),
                        'sleep': config.getint('fetcher', 'sleep.interval'),
                        'min_space': config.getfloat('fetcher', 'min.space'),
                        'executors': config.get('fetcher', 'valid.executors').split(',')}}

        return parsed_config

    def print_status(self):
        pass
        # TODO needs reworking

        # extract image names of running containers
        containers = ""
        for c in self.container_handler.running_containers:
            containers += c.attrs['Config']['Image'] + '\t'

        # clear std out
        # os.system('clear')

        # construct status string
        status_str = ('dop-q status:\t' + time.ctime() +
                      '\n\n\tfetcher status:\t' + self.fetcher.status +
                      '\n\tbuilder status:\t' + self.builder.status +
                      '\n\trunning containers:\t' + containers +
                      '\n\tused gpu minors:\t' + str(self.gpu_handler.assigned_minors) +
                      '\n\tfree gpu minors:\t' + str(self.gpu_handler.free_minors))
        if self.debug:
            status_str += '\n\timage list:\t' + str(self.container_list) + \
                          '\n\thistory:\t' + str(self.history)

        # print status message
        print(status_str)

        return status_str

    def stop(self):

        self.provider.stop()
        self.update_container_list()
        self.save_history()
        self.save_container_list()

    def run_queue(self):
        """
        Runs the priority queue.

        :return: None
        """

        # TODO: rewrite this method so that ir runs in a seperate process and the queue is able to respond to user inputs

        # start fetcher and builder
        p = self.provider.start()
        self.logger.info(time.ctime() + '\t started provider process, PID={}'.format(p))
        time.sleep(5)

        try:
            # run this until forced to quit
            while True:

                # update container list
                self.update_container_list()

                # print queue status
                # TODO move this to self.sleep()
                self.print_status()

                # check if there are containers in the queue
                if len(self.container_list) == 0:
                    self.sleep()
                    continue

                # get next container
                container = self.container_list.pop(0)
                gpu = container.use_gpu()

                # keep cycling if container requires gpu but none are available
                free_minors = self.gpu_handler.free_minors
                if len(free_minors) == 0 and gpu:
                    self.container_list.insert(0, container)
                    self.sleep()
                    continue

                # get next container
                container = self.container_list.pop(0)
                user = self.get_user(container)
                gpu_minor = free_minors.pop()

                try:
                    # TODO implement container logging and make sure starting the container returns the logging process
                    p = container.start()
                except IOError as e:
                    # put container back in the queue if not enough gpus are available
                    self.container_list.insert(0, container)
                    continue
                else:
                    # TODO
                    self.logger.info(time.ctime() + '\tsuccessfully ran a container from {}'
                                                    '\n\tcontainer logs are acquired in process {}'
                                     .format(container, p.pid))
                    # update history
                    self.history = [user] + self.history
                    self.history = self.history[:self.config['queue']['max_history']]

                    self.sleep()

        except Exception as e:
            self.logger.error(time.ctime() + '\tan error occured during the execution of the queue:\n\t\t{}'.format(e))

        finally:
            self.stop()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="priority queue for running docker containers")
    parser.add_argument('-l', '--logfile', type=str, dest='logfile', metavar='filename', default='queue.log')
    parser.add_argument('-c', '--config', type=str, dest='configfile', metavar='filename', default='config.ini')
    parser.add_argument('--debug', action='store_true')

    args = vars(parser.parse_args())

    # init logging
    log.init_log()

    dop_q = DopQ(**args)
    dop_q.run_queue()
