from invoke import task
from .commands import yarn, aws
from .util import chdir

WORKING_DIR = 'jdorg'


@task
def install(c):
    """Install all the client's dependencies."""
    with chdir(WORKING_DIR):
        yarn('install')
        yarn('audit')


@task
def upgrade(c):
    """Upgrade all the client's dependencies."""
    with chdir(WORKING_DIR):
        yarn('upgrade', '--latest')


@task(install)
def start(c):
    """Start the client in development mode, with hot reloading."""
    with chdir(WORKING_DIR):
        yarn('start')


@task(install)
def build(c):
    """Build the client."""
    with chdir(WORKING_DIR):
        yarn('build')


@task(install)
def test(c):
    """Run all the tests for the client."""
    with chdir(WORKING_DIR):
        yarn('test')


@task(build, help={
    "profile": "A valid AWS profile."
})
def deploy(c, profile):
    """Deploy client to S3."""
    with chdir(WORKING_DIR):
        aws('s3', 'sync', 'build',
            's3://www.joshuaduffy.org',
            '--delete',
            '--cache-control', 'no-cache,no-store,must-revalidate',
            f'--profile', f'{profile}')
        aws('s3', 'cp',
            's3://www.joshuaduffy.org/static',
            's3://www.joshuaduffy.org/static',
            '--recursive',
            '--metadata-directive', 'REPLACE',
            '--cache-control', 'public,max-age=31536000',
            f'--profile', f'{profile}')
        aws('s3', 'cp',
            's3://www.joshuaduffy.org/service-worker.js',
            's3://www.joshuaduffy.org/service-worker.js',
            '--metadata-directive', 'REPLACE',
            '--cache-control', 'no-cache,no-store,must-revalidate',
            '--content-type', 'application/javascript',
            f'--profile', f'{profile}')
