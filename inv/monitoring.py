from os import remove
from invoke import task
from .commands import docker_compose
from .util import chdir

WORKING_DIR = 'monitoring'


@task(help={
    "access-key": "A valid AWS access key.",
    "secret-key": "A valid AWS secret key."
})
def up(c, access_key=None, secret_key=None):
    """Builds, creates/re-creates and starts the grafana container."""
    with chdir(WORKING_DIR):
        remove('credentials')
        if access_key and secret_key:
            __create_credentials_file(access_key, secret_key)
        docker_compose('up', '--force-recreate', '--renew-anon-volumes')


def __create_credentials_file(access_key, secret_key):
    config = [
        '[default]',
        f'aws_access_key_id = {access_key}',
        f'aws_secret_access_key = {secret_key}'
    ]
    with open('credentials', 'w') as creds:
        creds.write('\n'.join(config))
