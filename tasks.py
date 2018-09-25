from os import path, listdir
from invoke import task

HERE = path.abspath(path.dirname(path.realpath(__file__)))
INFRA = path.abspath(path.join(HERE, 'infra'))
JDORG = path.abspath(path.join(HERE, 'jdorg'))
ROUTE53_ZONE_TEMPLATE = path.join(INFRA, 'zone.yaml')
ROUTE53_RECORDS_TEMPLATE = path.join(INFRA, 'mail.yaml')
CLOUDFORMATION_TEMPLATE = path.join(INFRA, 'static-site.yaml')


@task
def clean(c):
    """Remove all build artifacts."""
    c.run("docker run --rm -v {0}/:/jdorg alpine \
        rm -rf /jdorg/build".format(JDORG))


@task
def install(c):
    """Install packages."""
    c.run("cd jdorg && yarn install")


@task
def build(c):
    """Build the application."""
    c.run("cd jdorg && yarn build")


@task
def start(c):
    """Start the application, in development mode."""
    c.run("cd jdorg && yarn start")


@task
def test(c):
    """Run the tests."""
    c.run("cd jdorg && yarn test")


@task
def up(c):
    """Build and run the application."""
    c.run("docker-compose -f {0}/docker-compose.yaml up".format(HERE))


@task
def down(c):
    """Teardown the application."""
    c.run("docker-compose -f {0}/docker-compose.yaml down".format(HERE))


@task
def validate_cf(c, profile):
    """Validate all CloudFormation templates."""
    for filename in listdir(INFRA):
        c.run("aws cloudformation validate-template \
            --template-body file://{0} \
            --profile {1}".format(path.join(INFRA, filename), profile))


@task
def create_frontend_cf(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Create the frontend CloudFormation stack."""
    __create_update_stack(c, domain_name, full_domain_name,
                          acm_certificate_arn, profile)


@task
def update_frontend_cf(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Update the frontend CloudFormation stack."""
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
        --stack-name {6}-frontend \
        --template-body file://{1} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={2} \
            ParameterKey=FullDomainName,ParameterValue={3} \
            ParameterKey=AcmCertificateArn,ParameterValue={4} \
        --profile {5}".format(action, CLOUDFORMATION_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile, stack_name))


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
