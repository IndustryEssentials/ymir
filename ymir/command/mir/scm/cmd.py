#    Modified on GitPython CMD wrapper:
#    https://github.com/gitpython-developers/GitPython/blob/master/git/cmd.py

import io
import logging
import os
import signal
from subprocess import (Popen, PIPE)
import sys
import threading
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

from mir.scm.base import BaseScm


def dashify(string: str) -> str:
    return string.replace('_', '-')


def expand_path(pth: str, expand_vars: bool = True) -> str:
    try:
        pth = os.path.expanduser(pth)
        if expand_vars:
            pth = os.path.expandvars(pth)
        return os.path.normpath(os.path.abspath(pth))
    except Exception as e:
        logging.error(f"expand_path: error occured: {pth}, {e}")
        return ''


def safe_decode(bin_str: Union[bytes, str]) -> str:
    """Safely decodes a binary string to unicode"""
    if isinstance(bin_str, str):
        return bin_str
    if isinstance(bin_str, bytes):
        return bin_str.decode(sys.getfilesystemencoding(), 'surrogateescape')
    if bin_str is not None:
        raise TypeError('Expected bytes or text, but got %r' % (bin_str, ))
    return None


def stream_copy(source: Any, destination: Any, chunk_size: int = 512 * 1024) -> int:
    """Copy all data from the source stream into the destination stream in chunks
    of size chunk_size
    :return: amount of bytes written"""
    byte_read = 0
    while True:
        chunk = source.read(chunk_size)
        destination.write(chunk)
        byte_read += len(chunk)
        if len(chunk) < chunk_size:
            break
    # END reading output stream
    return byte_read


def find_root(root: str = None) -> str:
    root_dir = os.path.realpath(root or os.curdir)

    if not os.path.isdir(root_dir):
        raise ValueError("directory %s does not exist" % root_dir)

    return root_dir


def transform_kwarg(name: str, value: Any, split_single_char_options: bool) -> list:
    if len(name) == 1:
        if value is True:
            return ["-%s" % name]
        if value not in (False, None):
            if split_single_char_options:
                return ["-%s" % name, "%s" % value]
            return ["-%s%s" % (name, value)]
    else:
        if value is True:
            return ["--%s" % dashify(name)]
        if value is not False and value is not None:
            return ["--%s=%s" % (dashify(name), value)]
    return []


def transform_kwargs(split_single_char_options: bool = True, **kwargs: Any) -> list:
    """Transforms Python style kwargs into git command line options."""
    args = []
    kwargs = OrderedDict(sorted(kwargs.items(), key=lambda x: x[0]))
    for k, vals in kwargs.items():
        if isinstance(vals, (list, tuple)):
            for value in vals:
                args += transform_kwarg(k, value, split_single_char_options)
        else:
            args += transform_kwarg(k, vals, split_single_char_options)
    return args


execute_kwargs = {
    'istream', 'with_extended_output', 'with_exceptions', 'as_process', 'stdout_as_string', 'output_stream',
    'with_stdout', 'kill_after_timeout', 'universal_newlines', 'shell', 'env', 'max_chunk_size'
}


class CmdScm(BaseScm):
    """
    The Git class manages communication with the Git binary.
    It provides a convenient interface to calling the Git binary, such as in::
     g = Git( git_dir )
     g.init()                   # calls 'git init' program
     rval = g.ls_files()        # calls 'git ls-files' program
    ``Debugging``
        Set the GIT_PYTHON_TRACE environment variable print each invocation
        of the command to stdout.
        Set its value to 'full' to see details about the returned values.
    """
    def __init__(self, working_dir: str = None, scm_executable: str = None):
        """Initialize this instance with:
        :param working_dir:
           Git directory we should work in. If None, we always work in the current
           directory as returned by os.getcwd().
           It is meant to be the working tree directory if available, or the
           .git directory in case of bare repositories.
        :param scm_excutable: either git.
        """

        self._working_dir = find_root(working_dir)

        # self._working_dir = expand_path(working_dir)
        self._scm_executable = scm_executable

    def __getattr__(self, name: str) -> Any:
        """A convenience method as it allows to call the command as if it was
        an object.
        :return: Callable object that will execute call _call_process with your arguments."""
        if name[0] == '_':
            return BaseScm.__getattr__(self, name)
        return lambda *args, **kwargs: self._call_process(name, *args, **kwargs)

    @property
    def working_dir(self) -> str:
        """:return: Git directory we are working on"""
        return self._working_dir

    def execute(self,
                command: str,
                istream: Any = None,
                with_extended_output: bool = False,
                with_exceptions: bool = True,
                output_stream: Any = None,
                stdout_as_string: bool = True,
                kill_after_timeout: Any = None,
                with_stdout: bool = True,
                universal_newlines: bool = False,
                env: Any = None,
                max_chunk_size: Any = io.DEFAULT_BUFFER_SIZE,
                **subprocess_kwargs: Any) -> Optional[Union[str, tuple]]:
        """Handles executing the command on the shell and consumes and returns
        the returned information (stdout)
        :param command:
            The command argument list to execute.
            It should be a string, or a sequence of program arguments. The
            program to execute is the first item in the args sequence or string.
        :param istream:
            Standard input filehandle passed to subprocess.Popen.
        :param with_extended_output:
            Whether to return a (status, stdout, stderr) tuple.
        :param with_exceptions:
            Whether to raise an exception when git returns a non-zero status.
        :param output_stream:
            If set to a file-like object, data produced by the git command will be
            output to the given stream directly. Processes will
            always be created with a pipe due to issues with subprocess.
            This merely is a workaround as data will be copied from the
            output pipe to the given output stream directly.
            Judging from the implementation, you shouldn't use this flag !
        :param stdout_as_string:
            if False, the commands standard output will be bytes. Otherwise, it will be
            decoded into a string using the default encoding (usually utf-8).
            The latter can fail, if the output contains binary data.
        :param env:
            A dictionary of environment variables to be passed to `subprocess.Popen`.
        :param max_chunk_size:
            Maximum number of bytes in one chunk of data passed to the output_stream in
            one invocation of write() method. If the given number is not positive then
            the default value is used.
        :param subprocess_kwargs:
            Keyword arguments to be passed to subprocess.Popen. Please note that
            some of the valid kwargs are already set by this method, the ones you
            specify may not be the same ones.
        :param with_stdout: If True, default True, we open stdout on the created process
        :param universal_newlines:
            if True, pipes will be opened as text, and lines are split at
            all known line endings.
        :param kill_after_timeout:
            To specify a timeout in seconds for the git command, after which the process
            should be killed. It is
            set to None by default and will let the process run until the timeout is
            explicitly specified. This feature is not supported on Windows. It's also worth
            noting that kill_after_timeout uses SIGKILL, which can have negative side
            effects on a repository. For example, stale locks in case of git gc could
            render the repository incapable of accepting changes until the lock is manually
            removed.
        :return:
            * str(output) if extended_output = False (Default)
            * tuple(int(status), str(stdout), str(stderr)) if extended_output = True
            if output_stream is True, the stdout value will be your output stream:
            * output_stream if extended_output = False
            * tuple(int(status), output_stream, str(stderr)) if extended_output = True
            Note git is executed with LC_MESSAGES="C" to ensure consistent
            output regardless of system language.
        :raise GitCommandError:
        :note:
           If you add additional keyword arguments to the signature of this method,
           you must update the execute_kwargs tuple housed in this module."""

        logging.debug("{}: {}".format(self.working_dir, ' '.join(command)))

        # Allow the user to have the command executed in their working dir.
        cwd = self._working_dir or os.getcwd()

        # Start the process
        inline_env = env
        env = os.environ.copy()
        # Attempt to force all output to plain ascii english, which is what some parsing code
        # may expect.
        # According to stackoverflow (http://goo.gl/l74GC8), we are setting LANGUAGE as well
        # just to be sure.
        env["LANGUAGE"] = "C"
        env["LC_ALL"] = "C"
        env.update()
        if inline_env is not None:
            env.update(inline_env)

        if sys.version_info[0] > 2:
            cmd_not_found_exception = FileNotFoundError  # NOQA # exists, flake8 unknown @UndefinedVariable
        else:
            cmd_not_found_exception = OSError
        # end handle

        stdout_sink = (PIPE if with_stdout else None)
        try:
            proc = Popen(
                command,
                env=env,
                cwd=cwd,
                bufsize=-1,
                stdin=istream,
                stderr=PIPE,
                stdout=stdout_sink,
                close_fds=True,  # unsupported on windows
                universal_newlines=universal_newlines,
                creationflags=0,
                **subprocess_kwargs)
        except cmd_not_found_exception as err:
            raise ValueError(command, err) from err

        def _kill_process(pid: int) -> None:
            """ Callback method to kill a process. """
            process_id = Popen(['ps', '--ppid', str(pid)], stdout=PIPE)
            child_pids = []
            assert process_id.stdout is not None
            for line in process_id.stdout:
                if len(line.split()) > 0:
                    local_pid = (line.split())[0]
                    if local_pid.isdigit():
                        child_pids.append(int(local_pid))
            try:
                # Windows does not have SIGKILL, so use SIGTERM instead
                sig = getattr(signal, 'SIGKILL', signal.SIGTERM)
                os.kill(pid, sig)
                for child_pid in child_pids:
                    try:
                        os.kill(child_pid, sig)
                    except OSError:
                        pass
                kill_check.set()  # tell the main routine that the process was killed
            except OSError:
                # It is possible that the process gets completed in the duration after timeout
                # happens and before we try to kill the process.
                pass

        # end

        if kill_after_timeout:
            kill_check = threading.Event()
            watchdog = threading.Timer(kill_after_timeout, _kill_process, args=(proc.pid, ))

        # Wait for the process to return
        status = 0
        stdout_value = b''
        stderr_value = b''
        newline: Union[str, bytes] = "\n" if universal_newlines else b"\n"
        try:
            if output_stream is None:
                if kill_after_timeout:
                    watchdog.start()
                stdout_value, stderr_value = proc.communicate()
                if kill_after_timeout:
                    watchdog.cancel()
                    if kill_check.is_set():
                        stderr_value = str.encode(('Timeout: the command "%s" did not complete in %d '
                                                   'secs.' % (" ".join(command), kill_after_timeout)))
                        if not universal_newlines:
                            stderr_value = stderr_value.decode().encode(sys.getfilesystemencoding())
                # strip trailing "\n"
                if stdout_value and stdout_value.endswith(newline):  # type: ignore
                    stdout_value = stdout_value[:-1]
                if stderr_value and stderr_value.endswith(newline):  # type: ignore
                    stderr_value = stderr_value[:-1]
                status = proc.returncode
            else:
                max_chunk_size = max_chunk_size if max_chunk_size and max_chunk_size > 0 else io.DEFAULT_BUFFER_SIZE
                stream_copy(proc.stdout, output_stream, max_chunk_size)
                assert proc.stdout is not None
                stdout_value = proc.stdout.read()
                assert proc.stderr is not None
                stderr_value = proc.stderr.read()
                # strip trailing "\n"
                if stderr_value.endswith(newline):  # type: ignore
                    stderr_value = stderr_value[:-1]
                status = proc.wait()
            # END stdout handling
        finally:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()

        # # Keep this code incase we need to print debug infos.
        # if self.GIT_PYTHON_TRACE == 'full':
        #     cmdstr = " ".join(command)

        #     def as_text(stdout_value):
        #         return not output_stream and safe_decode(stdout_value) or '<OUTPUT_STREAM>'
        #     # end

        #     if stderr_value:
        #         logging.info("%s -> %d; stdout: '%s'; stderr: '%s'",
        #                  cmdstr, status, as_text(stdout_value), safe_decode(stderr_value))
        #     elif stdout_value:
        #         logging.info("%s -> %d; stdout: '%s'", cmdstr, status, as_text(stdout_value))
        #     else:
        #         logging.info("%s -> %d", cmdstr, status)
        # # END handle debug printing

        if with_exceptions and status != 0:
            raise ValueError(command, status, stderr_value, stdout_value)

        stdout_value_str: Optional[str] = None
        if isinstance(stdout_value, bytes) and stdout_as_string:  # could also be output_stream
            stdout_value_str = safe_decode(stdout_value)
        elif isinstance(stdout_value, str) and stdout_as_string:
            stdout_value_str = stdout_value
        else:
            stdout_value_str = ''

        # Allow access to the command's status code
        if with_extended_output:
            return (status, stdout_value_str, safe_decode(stderr_value))
        return stdout_value_str

    @classmethod
    def __unpack_args(cls, arg_list: Any) -> List[str]:
        if not isinstance(arg_list, (list, tuple)):
            return [str(arg_list)]

        outlist = []
        for arg in arg_list:
            if isinstance(arg_list, (list, tuple)):
                outlist.extend(cls.__unpack_args(arg))
            # END recursion
            else:
                outlist.append(str(arg))
        # END for each arg
        return outlist

    def __call__(self, **kwargs: Dict) -> Any:
        """Specify command line options to the git executable
        for a subcommand call
        :param kwargs:
            is a dict of keyword arguments.
            these arguments are passed as in _call_process
            but will be passed to the git command rather than
            the subcommand.
        ``Examples``::
            git(work_tree='/tmp').difftool()"""
        self._git_options = transform_kwargs(split_single_char_options=True, **kwargs)
        return self

    def _call_process(self, method: str, *args: tuple, **kwargs: Dict) -> Any:
        """Run the given git command with the specified arguments and return
        the result as a String
        :param method:
            is the command. Contained "_" characters will be converted to dashes,
            such as in 'ls_files' to call 'ls-files'.
        :param args:
            is the list of arguments. If None is included, it will be pruned.
            This allows your commands to call git more conveniently as None
            is realized as non-existent
        :param kwargs:
            It contains key-values for the following:
            - the :meth:`execute()` kwds, as listed in :var:`execute_kwargs`;
            - "command options" to be converted by :meth:`transform_kwargs()`;
            - the `'insert_kwargs_after'` key which its value must match one of ``*args``,
              and any cmd-options will be appended after the matched arg.
        Examples::
            git.rev_list('master', max_count=10, header=True)
        turns into::
           git rev-list max-count 10 --header master
        :return: Same as ``execute``"""
        # Handle optional arguments prior to calling transform_kwargs
        # otherwise these'll end up in args, which is bad.
        exec_kwargs = {k: v for k, v in kwargs.items() if k in execute_kwargs}
        opts_kwargs = {k: v for k, v in kwargs.items() if k not in execute_kwargs}

        insert_after_this_arg = opts_kwargs.pop('insert_kwargs_after', None)

        # Prepare the argument list
        opt_args = transform_kwargs(**opts_kwargs)  # type: ignore
        ext_args = self.__unpack_args([a for a in args if a is not None])

        if insert_after_this_arg is None:
            args_str = opt_args + ext_args  # type: ignore
        else:
            assert isinstance(insert_after_this_arg, str)
            try:
                index = ext_args.index(insert_after_this_arg)
            except ValueError as err:
                raise ValueError("Couldn't find argument '%s' in args %s to insert cmd options after" %
                                 (insert_after_this_arg, str(ext_args))) from err
            # end handle error
            assert isinstance(opt_args, list)
            args_str = ext_args[:index + 1] + opt_args + ext_args[index + 1:]
        # end handle opts_kwargs

        call = [self._scm_executable]

        call.append(dashify(method))
        call.extend(args_str)

        return self.execute(call, **exec_kwargs)  # type: ignore
