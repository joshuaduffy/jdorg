from os import path
from invoke import task

HERE = path.abspath(path.dirname(path.realpath(__file__)))
JDORG = path.abspath(path.join(HERE, 'jdorg'))
ROUTE53_ZONE_TEMPLATE = path.join(HERE, 'infra', 'zone.yaml')
CLOUDFORMATION_TEMPLATE = path.join(HERE, 'infra', 'static-site.yaml')


@task
def clean(c):
    """Remove all build artifacts."""
    c.run(
        "docker run --rm -v {0}/:/jdorg alpine rm -rf /jdorg/build".format(JDORG))


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
def validate(c, profile):
    """Validate the applications CloudFormation templates."""
    c.run("aws cloudformation validate-template \
        --template-body file://{0} \
        --profile {1}".format(ROUTE53_ZONE_TEMPLATE, profile))
    c.run("aws cloudformation validate-template \
        --template-body file://{0} \
        --profile {1}".format(CLOUDFORMATION_TEMPLATE, profile))


@task
def create(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Create the applications CloudFormation stack."""
    c.run("aws cloudformation create-stack \
        --stack-name {1} \
        --template-body file://{0} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={1} \
        --profile {2}".format(ROUTE53_ZONE_TEMPLATE, domain_name, profile))
    c.run("aws cloudformation create-stack \
        --stack-name {1} \
        --template-body file://{0} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={1} \
            ParameterKey=FullDomainName,ParameterValue={2} \
            ParameterKey=AcmCertificateArn,ParameterValue={3} \
        --profile {4}".format(CLOUDFORMATION_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile))


@task
def update(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Update the applications CloudFormation stack."""
    c.run("aws cloudformation update-stack \
        --stack-name {1} \
        --template-body file://{0} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={1} \
        --profile {2}".format(ROUTE53_ZONE_TEMPLATE, domain_name, profile))
    c.run("aws cloudformation update-stack \
        --stack-name {1} \
        --template-body file://{0} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={1} \
            ParameterKey=FullDomainName,ParameterValue={2} \
            ParameterKey=AcmCertificateArn,ParameterValue={3} \
        --profile {4}".format(CLOUDFORMATION_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile))
