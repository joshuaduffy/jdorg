from os import environ, remove, path
from invoke import task
from .commands import aws, docker
from .util import chdir
import yaml

WORKING_DIR = 'monitoring'


@task(help={
    "access-key": "A valid AWS access key.",
    "secret-key": "A valid AWS secret key."
})
def up(c, access_key=None, secret_key=None):
    """Builds, creates/re-creates and starts the grafana container."""
    with chdir(WORKING_DIR):
        if access_key and secret_key:
            try:
                remove('credentials')
            except:
                pass

            __create_credentials_file(access_key, secret_key)
            __update_auth_type(
                authType='credentials',
                defaultRegion='eu-west-1'
            )

        docker('build', '-t', 'grafana', '.')
        docker('run', '-p', '3000:3000', 'grafana')


@task(help={
    "profile": "A valid AWS profile."
})
def push(c, profile, aws_account_id='380760145297', aws_region='eu-west-1', ecr_repo_name='joshuaduffy-graf-ecr', tag='latest'):
    """Build and push the container to ECR"""
    c.run(aws('ecr', 'get-login', '--registry-ids', aws_account_id, '--no-include-email', '--profile', profile).stdout)

    with chdir(WORKING_DIR):
        with open('credentials', 'w') as creds:
            creds.write('\n')

        __update_auth_type(
            authType='arn',
            assumeRoleArn=f'arn:aws:iam::{aws_account_id}:role/joshuaduffy-graf-exec-rol',
            defaultRegion='eu-west-1'
        )

        docker('build', '-t', f'{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo_name}:{tag}', '.')
        docker('push', f'{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo_name}:{tag}')


def __create_credentials_file(access_key, secret_key):
    config = [
        '[default]',
        f'aws_access_key_id = {access_key}',
        f'aws_secret_access_key = {secret_key}'
    ]
    with open('credentials', 'w') as creds:
        creds.write('\n'.join(config))


def __update_auth_type(*args, **kwargs):
    with open(path.join('provisioning', 'datasources', 'all.yaml'), 'r') as datasource:
        transformed_datasource = yaml.load(datasource)
        transformed_datasource['datasources'][0]['jsonData'] = kwargs
    with open(path.join('provisioning', 'datasources', 'all.yaml'), 'w') as datasource:
        yaml.dump(transformed_datasource, datasource, default_flow_style=False)
