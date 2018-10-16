from os import path, listdir
from invoke import task

HERE = path.abspath(path.dirname(path.realpath(__file__)))

INFRA_FOLDER = path.join(HERE, 'infra')
JDORG_FOLDER = path.join(HERE, 'jdorg')

ROUTE53_ZONE_TEMPLATE = path.join(INFRA_FOLDER, 'zone.yaml')
ROUTE53_RECORDS_TEMPLATE = path.join(INFRA_FOLDER, 'mail.yaml')
CERT_TEMPLATE = path.join(INFRA_FOLDER, 'cert.yaml')
CLIENT_TEMPLATE = path.join(INFRA_FOLDER, 'static-site.yaml')


@task
def install(c):
    """Install all packages."""
    c.run("cd jdorg && yarn install")
    c.run("pipenv install")
    c.run("pipenv install --dev")


@task
def client_dev(c):
    """Start the API, then the client in development mode, with hot reloading."""
    c.run("docker-compose -f {0}/docker-compose.yaml up -d api".format(HERE))
    c.run("cd jdorg && yarn start")


@task
def api_dev(c):
    """Start the client, then the API in development mode, with hot reloading."""
    c.run("docker-compose -f {0}/docker-compose.yaml up -d client".format(HERE))
    c.run("cd api && python main.py")


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
def test(c):
    """Run all the tests."""
    c.run("cd jdorg && yarn test")


@task
def deploy(c, profile):
    """Deploy static files to S3."""
    __build(c)
    c.run("cd {0} && aws s3 sync build s3://www.joshuaduffy.org/ \
        --delete \
        --cache-control no-cache,no-store,must-revalidate \
        --profile {1}".format(JDORG_FOLDER, profile))
    c.run("aws s3 cp s3://www.joshuaduffy.org/static s3://www.joshuaduffy.org/static \
        --recursive \
        --metadata-directive REPLACE \
        --cache-control public,max-age=31536000 \
        --profile {0}".format(profile))


@task
def validate_cf(c, profile):
    """Validate all CloudFormation templates."""
    for filename in listdir(INFRA_FOLDER):
        c.run("aws cloudformation validate-template \
            --template-body file://{0} \
            --profile {1}".format(path.join(INFRA_FOLDER, filename), profile))


@task
def create_client_cf(c, stack_name, subdomain, profile, cert_arn=""):
    """Create the client CloudFormation stack."""
    __create_update_stack(c, stack_name, subdomain, profile, cert_arn)


@task
def update_client_cf(c, stack_name, subdomain, profile, cert_arn=""):
    """Update the client CloudFormation stack."""
    __create_update_stack(c, stack_name, subdomain, profile, cert_arn, create=False)


@task
def create_dns_cf(c, stack_name, domain_name, profile):
    """Create the DNS CloudFormation stack."""
    __create_update_dns(c, stack_name, domain_name, profile)


@task
def update_dns_cf(c, stack_name, domain_name, profile):
    """Update the DNS CloudFormation stack."""
    __create_update_dns(c, stack_name, domain_name, profile, create=False)


@task
def create_cert_cf(c, stack_name, domain_name, profile):
    """Create the SSL/TLS certificate CloudFormation stack."""
    __create_update_cert(c, stack_name, domain_name, profile)


@task
def update_cert_cf(c, stack_name, domain_name, profile):
    """Update the SSL/TLS certificate CloudFormation stack."""
    __create_update_cert(c, stack_name, domain_name, profile, create=False)


def __create_update_stack(c, stack_name, subdomain, profile, cert_arn, create=True):
    action = 'create' if create else 'update'

    c.run("aws cloudformation {0}-stack \
        --stack-name {1}-client \
        --template-body file://{2} \
        --parameters \
            ParameterKey=Subdomain,ParameterValue={3} \
            ParameterKey=CertificateArn,ParameterValue={4} \
        --profile {5}".format(action, stack_name, CLIENT_TEMPLATE, subdomain, cert_arn, profile))


def __create_update_dns(c, stack_name, domain_name, profile, create=True):
    action = 'create' if create else 'update'

    c.run("aws cloudformation {0}-stack \
        --stack-name {1}-dns \
        --template-body file://{2} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={3} \
        --profile {4}".format(action, stack_name, ROUTE53_ZONE_TEMPLATE, domain_name, profile))

    c.run("aws cloudformation wait stack-{0}-complete \
        --stack-name {1}-dns \
        --profile {2}".format(action, stack_name, profile))

    c.run("aws cloudformation {0}-stack \
        --stack-name {1}-dns-mail \
        --template-body file://{2} \
        --profile {3}".format(action, stack_name, ROUTE53_RECORDS_TEMPLATE, profile))


def __create_update_cert(c, stack_name, domain_name, profile, create=True):
    action = 'create' if create else 'update'

    c.run("aws cloudformation {0}-stack \
        --stack-name {1}-cert \
        --template-body file://{2} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={3} \
        --profile {4}".format(action, stack_name, CERT_TEMPLATE, domain_name, profile))

    # Cert also needs adding to us-east-1 to be used by CloudFront
    c.run("aws cloudformation {0}-stack \
        --stack-name {1}-cert \
        --template-body file://{2} \
        --parameters \
            ParameterKey=DomainName,ParameterValue={3} \
        --profile {4} \
        --region us-east-1".format(action, stack_name, CERT_TEMPLATE, domain_name, profile))


def __build(c):
    c.run("cd jdorg && yarn build")
