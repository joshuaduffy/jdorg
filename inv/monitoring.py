from os import environ, remove
from invoke import task
from .commands import docker_compose
from .util import chdir

WORKING_DIR = 'monitoring'


@task(help={
    "access-key": "A valid AWS access key.",
    "secret-key": "A valid AWS secret key.",
    "admin-user": "The name to give the admin user.",
    "admin-password": "The password for the admin user."
})
def up(c, admin_user, admin_password, access_key=None, secret_key=None):
    """Builds, creates/re-creates and starts the grafana container."""
    with chdir(WORKING_DIR):
        if access_key and secret_key:
            try:
                remove('credentials')
            except:
                pass
            __create_credentials_file(access_key, secret_key)

        environ.update({
            'ADMIN_USER': admin_user,
            'ADMIN_PASSWORD': admin_password
        })

        docker_compose('up', '--force-recreate', '--renew-anon-volumes')


def __create_credentials_file(access_key, secret_key):
    config = [
        '[default]',
        f'aws_access_key_id = {access_key}',
        f'aws_secret_access_key = {secret_key}'
    ]
    with open('credentials', 'w') as creds:
        creds.write('\n'.join(config))
