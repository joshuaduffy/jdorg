import os
from contextlib import contextmanager
from invoke import run
from shlex import quote
from shutil import which
from subprocess import list2cmdline
from platform import platform


@contextmanager
def chdir(dirname=None):
    """Change directory, then swap back to the original working directory."""
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


def command(exe=None, *args):
    """Construct a console command from a list of arguments."""
    executable = which(exe)
    if executable:
        return run(f'"{executable}" {__format_args(args)}')
    else:
        raise FileNotFoundError(exe)


def __format_args(*args):
    """Format the arguments for a console command."""
    if 'Windows' in platform():
        return list2cmdline(args)
    return ' '.join(map(quote, *args))
