from invoke import task
from .commands import docker_compose
from .util import chdir

WORKING_DIR = 'monitoring'


@task
def up(c):
    """Builds, creates/re-creates and starts the containers."""
    with chdir(WORKING_DIR):
        docker_compose('up')
