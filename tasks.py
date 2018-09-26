from os import path, listdir
from invoke import task

HERE = path.abspath(path.dirname(path.realpath(__file__)))

INFRA_FOLDER = path.join(HERE, 'infra')
JDORG_FOLDER = path.join(HERE, 'jdorg')

ROUTE53_ZONE_TEMPLATE = path.join(INFRA_FOLDER, 'zone.yaml')
ROUTE53_RECORDS_TEMPLATE = path.join(INFRA_FOLDER, 'mail.yaml')
CLIENT_TEMPLATE = path.join(INFRA_FOLDER, 'static-site.yaml')


@task
def install(c):
    """Install all packages."""
    c.run("cd jdorg && yarn install")
    c.run("pipenv install")
    c.run("pipenv install --dev")


@task
def yolo_deploy(c, profile):
    """You Only Live Once. Deploy build to S3 Bucket."""
    __build(c)
    c.run("cd {0} && aws s3 cp build s3://www.joshuaduffy.org/ \
        --recursive \
        --acl public-read \
        --profile {1}".format(JDORG_FOLDER, profile))


@task
def client_dev(c):
    """Start the API, then the client in development mode, with hot reloading."""
    c.run("docker-compose -f {0}/docker-compose.yaml up -d api".format(HERE))
    c.run("cd jdorg && yarn start")


@task
def test(c):
    """Run the tests."""
    c.run("cd jdorg && yarn test")


@task
def up(c):
    """Build and run the application."""
    __build(c)
    c.run("pipenv lock -r > ./api/requirements.txt")
    c.run("docker-compose -f {0}/docker-compose.yaml up -d".format(HERE))


@task
def down(c):
    """Teardown the application."""
    c.run("docker-compose -f {0}/docker-compose.yaml down".format(HERE))


@task
def validate_cf(c, profile):
    """Validate all CloudFormation templates."""
    for filename in listdir(INFRA_FOLDER):
        c.run("aws cloudformation validate-template \
            --template-body file://{0} \
            --profile {1}".format(path.join(INFRA_FOLDER, filename), profile))


@task
def create_client_cf(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Create the client CloudFormation stack."""
    __create_update_stack(c, domain_name, full_domain_name,
                          acm_certificate_arn, profile)


@task
def update_client_cf(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Update the client CloudFormation stack."""
    __create_update_stack(c, domain_name, full_domain_name,
                          acm_certificate_arn, profile, create=False)


@task
def create_dns_cf(c, domain_name, profile):
    """Create the DNS CloudFormation stack."""
    __create_update_dns(c, domain_name, profile)


@task
def update_dns_cf(c, domain_name, profile):
    """Update the DNS CloudFormation stack."""
    __create_update_dns(c, domain_name, profile, create=False)


def __create_update_stack(c, domain_name, full_domain_name, acm_certificate_arn, profile, create=True):
    action = 'create' if create else 'update'
    stack_name = domain_name.split('.')[0]

    c.run("aws cloudformation {0}-stack \
        --stack-name {6}-client \
        --template-body file://{1} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={2} \
            ParameterKey=FullDomainName,ParameterValue={3} \
            ParameterKey=AcmCertificateArn,ParameterValue={4} \
        --profile {5}".format(action, CLIENT_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile, stack_name))


def __create_update_dns(c, domain_name, profile, create=True):
    action = 'create' if create else 'update'
    stack_name = domain_name.split('.')[0]

    c.run("aws cloudformation {0}-stack \
        --stack-name {4}-dns \
        --template-body file://{1} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={2} \
        --profile {3}".format(action, ROUTE53_ZONE_TEMPLATE, domain_name, profile, stack_name))
    
    c.run("aws cloudformation wait stack-{0}-complete \
        --stack-name {2}-dns \
        --profile {1}".format(action, profile, stack_name))

    c.run("aws cloudformation {0}-stack \
        --stack-name {4}-dns-mail \
        --template-body file://{1} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={2} \
        --profile {3}".format(action, ROUTE53_RECORDS_TEMPLATE, domain_name, profile, stack_name))

def __build(c):
    __clean(c)
    c.run("cd jdorg && yarn build")

def __clean(c):
    """Remove all build artifacts."""
    c.run("docker run --rm -v {0}/:/jdorg alpine \
        rm -rf /jdorg/build".format(JDORG_FOLDER))
