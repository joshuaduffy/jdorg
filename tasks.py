from os import path
from invoke import task

HERE = path.abspath(path.dirname(path.realpath(__file__)))
ROUTE53_ZONE_TEMPLATE = path.join(HERE, 'infra', 'zone.yaml')
CLOUDFORMATION_TEMPLATE = path.join(HERE, 'infra', 'static-site.yaml')


@task
def clean(c):
    """Remove all build artifacts."""
    c.run(
        "docker run --rm -v {HERE}/:/jdorg alpine rm -rf /jdorg/build".format(HERE))


@task
def install(c):
    """Install packages."""
    c.run("yarn install")


@task
def build(c):
    """Build the application."""
    c.run("yarn build")


@task
def start(c):
    """Start the application, in development mode."""
    c.run("yarn start")


@task
def test(c):
    """Run the tests."""
    c.run("yarn test")


@task
def up(c):
    """Build and run the application."""
    c.run("docker-compose -f {HERE}/docker-compose.yaml up".format(HERE))


@task
def down(c):
    """Teardown the application."""
    c.run("docker-compose -f {HERE}/docker-compose.yaml down".format(HERE))


@task
def validate(c, profile):
    """Validate the applications CloudFormation templates."""
    c.run("aws cloudformation validate-template \
        --template-body file://{ROUTE53_ZONE_TEMPLATE} \
        --profile {profile}".format(ROUTE53_ZONE_TEMPLATE, profile))
    c.run("aws cloudformation validate-template \
        --template-body file://{ROUTE53_ZONE_TEMPLATE} \
        --profile {profile}".format(CLOUDFORMATION_TEMPLATE, profile))


@task
def create(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Create the applications CloudFormation stack."""
    c.run("aws cloudformation create-stack \
        --stack-name {domain_name} \
        --template-body file://{ROUTE53_ZONE_TEMPLATE} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={domain_name} \
        --profile {profile}".format(ROUTE53_ZONE_TEMPLATE, domain_name, profile))
    c.run("aws cloudformation create-stack \
        --stack-name {domain_name} \
        --template-body file://{CLOUDFORMATION_TEMPLATE} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={domain_name} \
            ParameterKey=FullDomainName,ParameterValue={full_domain_name} \
            ParameterKey=AcmCertificateArn,ParameterValue={acm_certificate_arn} \
        --profile {profile}".format(CLOUDFORMATION_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile))


@task
def update(c, domain_name, full_domain_name, acm_certificate_arn, profile):
    """Update the applications CloudFormation stack."""
    c.run("aws cloudformation update-stack \
        --stack-name {domain_name} \
        --template-body file://{ROUTE53_ZONE_TEMPLATE} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={domain_name} \
        --profile {profile}".format(ROUTE53_ZONE_TEMPLATE, domain_name, profile))
    c.run("aws cloudformation update-stack \
        --stack-name {domain_name} \
        --template-body file://{CLOUDFORMATION_TEMPLATE} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={domain_name} \
            ParameterKey=FullDomainName,ParameterValue={full_domain_name} \
            ParameterKey=AcmCertificateArn,ParameterValue={acm_certificate_arn} \
        --profile {profile}".format(CLOUDFORMATION_TEMPLATE, domain_name, full_domain_name, acm_certificate_arn, profile))
