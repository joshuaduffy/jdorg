from os import environ, remove
from invoke import task
from .commands import docker_compose, docker, aws
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
    __update_env(admin_user, admin_password)

    with chdir(WORKING_DIR):
        if access_key and secret_key:
            try:
                remove('credentials')
            except:
                pass
            __create_credentials_file(access_key, secret_key)

        docker_compose('up', '--force-recreate', '--renew-anon-volumes')


@task(help={
    "admin-user": "The name to give the admin user.",
    "admin-password": "The password for the admin user.",
    "profile": "A valid AWS profile."
})
def push(c, profile, admin_user, admin_password, aws_account_id='380760145297', aws_region='eu-west-1', ecr_repo_name='joshuaduffy-graf-ecr', tag='latest'):
    """Build and push the container to ECR"""
    c.run(aws('ecr', 'get-login', '--registry-ids', aws_account_id, '--no-include-email', '--profile', profile).stdout)

    __update_env(admin_user, admin_password)

    with chdir(WORKING_DIR):
        docker_compose('push')


def __create_credentials_file(access_key, secret_key):
    config = [
        '[default]',
        f'aws_access_key_id = {access_key}',
        f'aws_secret_access_key = {secret_key}'
    ]
    with open('credentials', 'w') as creds:
        creds.write('\n'.join(config))


def __update_env(admin_user, admin_password):
    environ.update({
        'ADMIN_USER': admin_user,
        'ADMIN_PASSWORD': admin_password,
        'AWS_ACCOUNT_ID': '380760145297',
        'AWS_REGION': 'eu-west-1',
        'DOCKER_REPO': 'joshuaduffy-graf-ecr',
        'DOCKER_TAG': 'latest'
    })
