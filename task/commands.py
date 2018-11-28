
from .util import command


def yarn(*args):
    """Yarn command"""
    return command('yarn', *args)


def aws(*args):
    """AWS CLI command"""
    return command('aws', *args)
