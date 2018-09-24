from invoke import task
import os 

HERE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

@task
def clean(c):
    c.run("docker run --rm -v {0}/:/jdorg alpine rm -rf /jdorg/build".format(HERE))

@task
def build(c):
    c.run("docker run --rm -v {0}/:/jdorg -w /jdorg node npm run build".format(HERE))

@task
def start(c):
    c.run("docker run -v {0}/:/jdorg -w /jdorg node npm run start".format(HERE))

@task
def up(c):
    clean(c)
    build(c)
    c.run("docker-compose -f {0}/docker-compose.yaml up".format(HERE))

@task
def down(c):
    c.run("docker-compose -f {0}/docker-compose.yaml down".format(HERE))

@task
def teardown(c):
    ids = c.run("docker ps -aq")
    c.run("docker stop {0}".format(ids.stdout))
