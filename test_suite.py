import helper_process
from core import container, containerconfig
import utils.gpu
import time
import utils.interface
import numpy as np
from utils.cpu import CPU
import threading
import datetime


class DummyDoPQ(helper_process.HelperProcess):

    def __init__(self):
        super(DummyDoPQ, self).__init__()
        self.starttime = None
        self.running_containers = []
        self.provider = DummyProvider()
        self.user_list = ['dummy the dummy', 'simple dummy', 'Sir Dummington', 'dummy with no name']#,
                          #'360_no_dummy', 'swag_dummy', 'bla', 'last_one']

        self.history = []
        self.container_list = [DummyContainer('dummy', [0]),
                               DummyContainer('dummy', [1], 'Sir Dummington'),
                               DummyContainer('dummy', [2, 0], 'lazy_dummy_420', 'paused'),
                               DummyContainer('dummy', [1], 'Much Container! WOW!', 'exited')]
        self.paths = {'log': '.'}
        self.thread = threading.Thread(target=self.run_queue)

    @property
    def uptime(self):
        if self.starttime is None:
            return '0s'

        diff = time.time() - self.starttime

        # break down diff into seconds, minutes, hours and days
        diff, seconds = divmod(int(diff), 60)
        diff, minutes = divmod(diff, 60)
        days, hours = divmod(diff, 24)

        # convert information to print format
        uptime = ''
        uptime += '{}d '.format(days) if days else ''
        uptime += '{}h '.format(hours) if hours else ''
        uptime += '{}m '.format(minutes) if minutes else ''
        uptime += '{}s'.format(seconds) if not minutes else ''

        starttime = datetime.datetime.fromtimestamp(self.starttime).strftime("%a, %d.%b %H:%M")

        return uptime, starttime

    @property
    def status(self):

        if self.starttime is None:
            return 'not started'
        elif self.thread.isAlive():
            return 'running'
        else:
            return 'terminated'

    def generate_container_list(self, n, status):
        containers = []
        for i in range(n):
            user = self.user_list[np.random.randint(0, len(self.user_list))]
            containers.append(DummyContainer(user, status=status))
        return containers

    def reload_config(self, report_fn=None):

        # init report fn if not given
        if report_fn is None:
            report_fn = self.logger

        report_fn('reloading config: {:.1f} %'.format(0))
        time.sleep(3)

        # loading done
        report_fn('reloading config: {:.1f} %'.format(50))
        time.sleep(3)

        # loading done
        report_fn('reloading config: {:.1f} %'.format(100))
        time.sleep(3)

    def run_queue(self):
        try:
            while not self.term_flag.value:
                for container in self.container_list:
                    time.sleep(5)
                    self.running_containers += [container]
                    self.container_list.remove(container)

                for container in self.running_containers:
                    time.sleep(5)
                    self.history += [container]
                    self.running_containers.remove(container)
        finally:
            self.provider.stop()
            self.stop()

    def start(self):
        try:
            self.starttime = time.time()
            self.thread.start()
            utils.interface.run_interface(self)
        finally:
            self.stop()

    @property
    def users_stats(self):
        users = self.user_list
        user_stats = []

        # get info for all users
        for user in users:
            single_user_stats = {'user': user,
                                 'penalty': round(np.random.randn(1), 4),
                                 'containers run': self.find_user_in_containers(user, self.history),
                                 'containers enqueued': self.find_user_in_containers(user, self.container_list)}

            user_stats.append(single_user_stats)

        return user_stats

    @staticmethod
    def find_user_in_containers(user, container_list):
        """
        small helper for counting how many containers in the list belong to user
        :param user: name of the user
        :param container_list: list with Container objects
        :return: number of user's containers in container_list
        """

        num_containers = 0
        for container in container_list:
            if container.user == user:
                num_containers += 1

        return num_containers


class DummyContainer(object):

    def __init__(self, user, minors=[], name='dummy', status='running'):

        self.minors = minors
        self.name = name
        self.status = status
        self.user = user

    @property
    def use_gpu(self):
        return bool(self.minors)

    @property
    def docker_name(self):
        return 'mighty_mckenzie'

    def container_stats(self, runtime_stats=True):
        import psutil

        # build base info
        base_info = {'name': self.name, 'executor': self.user, 'run_time': 'forever', 'created': 'ancient times',
                     'docker name': self.docker_name, 'status': self.status}

        # also show runtime info?
        if runtime_stats:

            # cpu_stats = stats_dict['cpu_stats']
            cpu = CPU(interval=0.1)
            cpu_usage_percentage = cpu.cpu_percent()

            # calc memory usage
            mem_stats = {'usage': 20, 'limit': 100}
            mem_usage = mem_stats['usage'] * 100.0 / mem_stats['limit']

            # add base runtime info
            base_info.update({'cpu': cpu_usage_percentage, 'memory': mem_usage})

            # add gpu info, if required
            gpu_info = {}
            for minor in self.minors:
                gpu_info[str(minor)] = {'id': minor, 'usage': np.random.randint(0, 100)}

            base_info['gpu'] = [
                {'id': gpu_dt['id'], 'usage': gpu_dt['usage']}
                for gpu_dt in list(gpu_info.values())]

        return base_info

    def history_info(self):
        return self.container_stats(False)


class DummyProvider(helper_process.HelperProcess):

    def __init__(self):
        super(DummyProvider , self).__init__()
        self.start()

    def provide(self):
        while not self.term_flag.value:
            time.sleep(10)

    def start(self):
        super(DummyProvider, self).start(target=self.provide, name='DummyProvider')


if __name__ == '__main__':

    dopq = DummyDoPQ()
    dopq.start()


