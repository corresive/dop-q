#!/usr/bin/env python
# encoding: utf-8
"""
gpu.py

Helpers for GPU information retrieval
"""

import os
import re
import docker
import GPUtil
import time


class GPU(object):

    class __GPU(object):

        def __init__(self, interval=1):
            self.last_call = 0
            self.stats = 0
            self.interval = interval

        def gpu_stats(self):
            current_time = time.time()

            if current_time - self.last_call > self.interval:
                self.stats = GPUtil.getGPUs()
                self.last_call = current_time

            return self.stats

    instance = None

    def __init__(self, interval=1):

        if GPU.instance is None:
            GPU.instance = GPU.__GPU(interval)
        else:
            GPU.instance.interval = interval

    def gpu_stats(self):
        return GPU.instance.gpu_stats()


def get_system_gpus():
    """
    Returns the GPU minors available on the system
    :return: GPU minors available on the system
    """
    minors = []
    for dev in os.listdir("/dev"):
        match_dt = re.search(r'nvidia(\d+)', dev)
        if match_dt is not None:
            minor = int(match_dt.group(1))
            minors.append(minor)
    return minors


def get_assigned_gpus(client=None):
    """
    Updates assigned and free minors by looking at the running containers

    :param client: Docker API client.
    :return: None
    """

    # if there is no client
    if client is None:

        # get a client
        client = docker.from_env()

    # get system minors
    minors = get_system_gpus()

    # get assigned gpus
    assigned_gpus = []

    # look in each running container
    for container in client.containers.list():

        if 'Config' in container.attrs:
            if 'Env' in container.attrs['Config']:
                for el in container.attrs['Config']['Env']:
                    if el.startswith('NVIDIA_VISIBLE_DEVICES'):
                        minor_str = el.split('=')[1]
                        if minor_str.lower() == 'all':
                            for gpu_minor in minors:
                                assigned_gpus.append(gpu_minor)
                        else:
                            minor_list = minor_str.split(",")
                            for gpu_minor in minor_list:
                                gpu_minor = int(gpu_minor)
                                if gpu_minor in minors:
                                    assigned_gpus.append(gpu_minor)

    return assigned_gpus


def get_gpus_status(client=None):
    """
    Get free GPU minors.

    :param client: Docker API client.
    :return: A list with free GPU minors.
    """

    assigned_gpus = get_assigned_gpus(client)
    free_gpus = []

    # remove all assigned
    for gpu_minor in get_system_gpus():

        # only add unassigend ones
        if gpu_minor not in assigned_gpus:
            free_gpus.append(gpu_minor)

    return free_gpus, assigned_gpus


def get_gpu_infos(device_ids=None):
    """
    Provides a dictionary mapping each GPU minor (or requested) to all relevant information.

    :param device_ids: List or single GPU minor to include or None if all shall be shown.
    :return: Dictionary mapping each GPU minor to its information.
    """

    # cast to set if int
    if isinstance(device_ids, int):
        device_ids = {device_ids}
    elif isinstance(device_ids, str) or isinstance(device_ids, unicode):
        if device_ids == 'all':
            device_ids = None
    elif isinstance(device_ids, list) and (isinstance(device_ids[0], str) or isinstance(device_ids[0], unicode)):
        if device_ids == ['all']:
            device_ids = None

    gpu = GPU()
    gpu_list = gpu.gpu_stats()
    if device_ids is None:
        gpu_dict = dict([(gpu_i.id, gpu_i.__dict__) for gpu_i in gpu_list])
    else:
        gpu_dict = dict([(gpu_i.id, gpu_i.__dict__) for gpu_i in gpu_list if gpu_i.id in device_ids])

    return gpu_dict
