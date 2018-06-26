#!/usr/bin/env python
# encoding: utf-8
"""
container.py

Provides a wrapper for container objects
"""

# from docker.models.containers import Container as DockerContainer
# from core.containerconfig import ContainerConfig
import os
import time
from utils.gpu import get_gpus_status
from utils import log

LOG = log.get_module_log(__name__)


class Container:
    """
    Wrapper for docker container objects
    """

    def __init__(self, config, container_obj, log_dir=None):
        """
        Creates a new container instance.

        :param config: Provides a run configuration for the docker container.
        :param container_obj: The underlying docker container instance.
        """

        self.config = config
        self.container_obj = container_obj
        self.last_log_update = int(time.time())
        self.last_log_file_update = int(time.time())
        self.log_dir = log_dir if log_dir is not None else ""

    @property
    def created_at(self):
        """
        wrapper for getting the creation time of the container object
        :return: creation date and time as unicode
        """
        return self.container_obj.attrs['Created']

    @property
    def use_gpu(self):
        """
        helper for seeing if the container requires gpu
        :return True if use of gpus is specified in the ContainerConfig object
        """
        return bool(self.config.num_gpus)

    @property
    def user(self):
        """
        wrapper for accessing the username from the config
        :return: name of the executing user
        """
        return self.config.executor_name

    def name(self):
        """
        The name of the container.
        """
        return self.container_obj.name()

    def image(self):
        """
        The image of the container.
        """
        return self.container_obj.image()

    @property
    def status(self):
        """
        The status of the container. For example, ``running``, or ``exited``.
        """
        return self.container_obj.status

    def attach(self, **kwargs):
        """
        Attach to this container.

        :py:meth:`logs` is a wrapper around this method, which you can
        use instead if you want to fetch/stream container output without first
        retrieving the entire backlog.

        Args:
            stdout (bool): Include stdout.
            stderr (bool): Include stderr.
            stream (bool): Return container output progressively as an iterator
                of strings, rather than a single string.
            logs (bool): Include the container's previous output.

        Returns:
            By default, the container's output as a single string.

            If ``stream=True``, an iterator of output strings.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.attach(**kwargs)

    def exec_run(self, cmd, stdout=True, stderr=True, stdin=False, tty=False,
                 privileged=False, user='', detach=False, stream=False,
                 socket=False, environment=None):
        """
        Run a command inside this container. Similar to
        ``docker exec``.

        Args:
            cmd (str or list): Command to be executed
            stdout (bool): Attach to stdout. Default: ``True``
            stderr (bool): Attach to stderr. Default: ``True``
            stdin (bool): Attach to stdin. Default: ``False``
            tty (bool): Allocate a pseudo-TTY. Default: False
            privileged (bool): Run as privileged.
            user (str): User to execute command as. Default: root
            detach (bool): If true, detach from the exec command.
                Default: False
            stream (bool): Stream response data. Default: False
            socket (bool): Return the connection socket to allow custom
                read/write operations. Default: False
            environment (dict or list): A dictionary or a list of strings in
                the following format ``["PASSWORD=xxx"]`` or
                ``{"PASSWORD": "xxx"}``.

        Returns:
            (generator or str):
                If ``stream=True``, a generator yielding response chunks.
                If ``socket=True``, a socket object for the connection.
                A string containing response data otherwise.
        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.exec_run(cmd, stdout, stderr, stdin, tty, privileged, user, detach, stream,
                                           socket, environment)

    def start(self, **kwargs):
        # TODO extend start method. container can run itself since it contains all the necessary information
        """
        Start this container. Similar to the ``docker start`` command, but
        doesn't support attach options.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """

        # check status
        if self.status == 'running' or self.status == 'restarting':
            LOG.warning("Container is already running or restarting (status={}). "
                        "Calling start has no effect here!".format(self.status))
            return self

        # for non-paused containers
        if self.status != 'paused':

            # read number of requested GPUs from config
            n_gpus = self.config.num_gpus

            # gpus required?
            if n_gpus > 0:

                # get free gpus
                free_gpus, _ = get_gpus_status()

                # set minors
                if len(free_gpus) < n_gpus:

                    # report problem
                    raise IOError("Not enough GPUs available to run container "
                                  "(available={}, required={})!".format(len(free_gpus), n_gpus))

                # assign
                self.set_gpu_minors(free_gpus[:n_gpus])

            # start it
            return self.container_obj.start(**kwargs)

        else:

            LOG.warning("You should not call start to unpause a paused container!")
            return self.container_obj.unpause(**kwargs)

    def restart(self, **kwargs):
        """
        Restart this container. Similar to the ``docker restart`` command.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.restart(**kwargs)

    def pause(self):
        """
        Pauses all processes within this container.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.pause()

    def unpause(self):
        """
        Unpause all processes within the container.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.unpause()

    def stop(self):
        """
        Stops a container. Similar to the ``docker stop`` command.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.stop()

    def kill(self, signal=None):
        """
        Kill or send a signal to the container.

        Args:
            signal (str or int): The signal to send. Defaults to ``SIGKILL``

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.kill(signal)

    def get_archive(self, path):
        """
        Retrieve a file or folder from the container in the form of a tar
        archive.

        Args:
            path (str): Path to the file or folder to retrieve

        Returns:
            (tuple): First element is a raw tar data stream. Second element is
            a dict containing ``stat`` information on the specified ``path``.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.get_archive(path)

    def put_archive(self, path, data):
        """
        Insert a file or folder in this container using a tar archive as
        source.

        Args:
            path (str): Path inside the container where the file(s) will be
                extracted. Must exist.
            data (bytes): tar data to be extracted

        Returns:
            (bool): True if the call succeeds.

        Raises:
            :py:class:`~docker.errors.APIError` If an error occurs.
        """
        return self.container_obj.put_archive(path, data)

    def remove(self, **kwargs):
        """
        Remove this container. Similar to the ``docker rm`` command.

        Args:
            v (bool): Remove the volumes associated with the container
            link (bool): Remove the specified link and not the underlying
                container
            force (bool): Force the removal of a running container (uses
                ``SIGKILL``)

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.remove(**kwargs)

    def stats(self, **kwargs):
        """
        Stream statistics for this container. Similar to the
        ``docker stats`` command.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.stats(**kwargs)

    def top(self, **kwargs):
        """
        Display the running processes of the container.

        Returns:
            (str): The output of the top

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.top(**kwargs)

    def update(self, **kwargs):
        """
        Update resource configuration of the containers.

        Returns:
            (dict): Dictionary containing a ``Warnings`` key.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.update(**kwargs)

    def wait(self, **kwargs):
        """
        Block until the container stops, then return its exit code. Similar to
        the ``docker wait`` command.

        Returns:
            (int): The exit code of the container. Returns ``-1`` if the API
            responds without a ``StatusCode`` attribute.

        Raises:
            :py:class:`requests.exceptions.ReadTimeout`
                If the timeout is exceeded.
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.wait(**kwargs)

    def logs(self, **kwargs):
        """
        Get logs from this container. Similar to the ``docker logs`` command.

        The ``stream`` parameter makes the ``logs`` function return a blocking
        generator you can iterate over to retrieve log output as it happens.

        Args:
            stdout (bool): Get ``STDOUT``
            stderr (bool): Get ``STDERR``
            stream (bool): Stream the response
            timestamps (bool): Show timestamps
            tail (str or int): Output specified number of lines at the end of
                logs. Either an integer of number of lines or the string
                ``all``. Default ``all``
            since (datetime or int): Show logs since a given datetime or
                integer epoch (in seconds)
            follow (bool): Follow log output

        Returns:
            (generator or str): Logs from the container.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.logs(**kwargs)

    def export(self):
        """
        Export the contents of the container's filesystem as a tar archive.

        Returns:
            (str): The filesystem tar archive

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.container_obj.export()

    def set_gpu_minors(self, gpu_minors):
        """
        Sets the GPU minors in environment according to given list.

        :param gpu_minors: List with GPU minors to assign to container.
        :return: None
        """
        self.container_obj.attr['Config']['Env'] += ['NVIDIA_VISIBLE_DEVICES={}'.format(",".join(gpu_minors))]

    def append_new_logs(self):
        """
        Retrieves all updates since last check and writes it to log.
        :return: Number of new bytes
        """

        # get new logs
        new_logs = self.logs(stdout=True, stderr=True, since=self.last_log_update)

        # update
        self.last_log_update = int(time.time())

        # leave
        if len(new_logs) == 0:
            return 0

        # add to log
        LOG.info("Container '{}' status: ".format(self.name(), new_logs))

        # return the number of new bytes
        return len(new_logs)

    def append_new_logs_to_file(self, file_path=None):
        """
        Appends the newly created log data to given file path.

        :param file_path: Path for container log (if none, a name will be generated)
        :return: Number of new bytes
        """

        # if no file path has been given
        if file_path is None:

            # build file path
            file_path = os.path.join(self.log_dir, "{}_{}.log".format(self.name(), self.created_at))

        # get new logs
        new_logs = self.logs(stdout=True, stderr=True, since=self.last_log_file_update)

        # update
        self.last_log_file_update = int(time.time())

        # leave
        if len(new_logs) == 0:
            return 0

        # open in append mode and add
        with open(file_path, 'a+') as file_h:
            file_h.write(new_logs)

        # return the number of new bytes
        return len(new_logs)
