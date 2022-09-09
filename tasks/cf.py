from os import listdir
from invoke import task
from .commands import aws
from .util import chdir

WORKING_DIR = 'infra'


@task(help={
    "profile": "A valid AWS profile"
})
def validate(c, profile):
    """Validate CloudFormation templates"""
    with chdir(WORKING_DIR):
        for file in listdir():
            aws('cloudformation', 'validate-template',
                '--template-body', f'file://{file}',
                f'--profile', f'{profile}')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "domain-name": "The domain name to configure. (e.g. joshuaduffy.org)",
    "profile": "A valid AWS profile."
})
def update_dns(c, stack_name, domain_name, profile, create=False):
    """Create or update DNS CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-dns',
            '--template-body', f'file://zone.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile', f'{profile}')

    aws('cloudformation', 'wait',
        f'stack-{action}-complete',
        '--stack-name', f'{stack_name}-dns',
        f'--profile', f'{profile}')

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-dns-mail',
            '--template-body', f'file://mail.yaml',
            f'--profile', f'{profile}')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "domain-name": "The domain name to configure. (e.g. joshuaduffy.org)",
    "profile": "A valid AWS profile."
})
def update_cert(c, stack_name, domain_name, profile, create=False):
    """Create or update certificate CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-cert',
            '--template-body', f'file://cert.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile', f'{profile}')
        # Cert also needs adding to us-east-1 to be used by CloudFront
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-cert',
            '--template-body', f'file://cert.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile', f'{profile}',
            '--region', 'us-east-1')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "subdomain": "The subdomain to configure. (e.g. www)",
    "cert-arn": "A valid certificate ARN.",
    "profile": "A valid AWS profile."
})
def update_client(c, stack_name, subdomain, profile, cert_arn=None, create=False):
    """Create or update client/static site CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-client',
            '--template-body', f'file://static-site.yaml',
            '--parameters',
            f'ParameterKey=Subdomain,ParameterValue={subdomain}',
            f'ParameterKey=CertificateArn,ParameterValue={cert_arn if cert_arn else ""}',
            f'--profile', f'{profile}')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "fqdn": "The DNS name you wish to alias to the TLD. (e.g. www.joshuaduffy.org)",
    "cert-arn": "A valid certificate ARN.",
    "profile": "A valid AWS profile."
})
def update_tld_redirect(c, stack_name, fqdn, profile, cert_arn=None, create=False):
    """Create or update TLD redirect CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-dns-tld',
            '--template-body', f'file://top-level-domain.yaml',
            '--parameters',
            f'ParameterKey=FullyQualifiedDomainName,ParameterValue={fqdn}',
            f'ParameterKey=CertificateArn,ParameterValue={cert_arn if cert_arn else ""}',
            f'--profile', f'{profile}')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "profile": "A valid AWS profile."
})
def update_vpc(c, stack_name, profile, create=False):
    """Create or update VPC CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-vpc',
            '--template-body', f'file://vpc.yaml',
            f'--profile', f'{profile}')


@task(help={
    "stack-name": "The name to prefix before the stack.",
    "subdomain": "The subdomain to configure. (e.g. www)",
    "cert-arn": "A valid certificate ARN.",
    "profile": "A valid AWS profile."
})
def update_monitoring(c, stack_name, subdomain, profile, cert_arn=None, create=False):
    """Create or update monitoring CloudFormation stack"""
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            '--stack-name', f'{stack_name}-monitoring',
            '--template-body', f'file://monitoring.yaml',
            '--capabilities', 'CAPABILITY_NAMED_IAM',
            '--parameters',
            f'ParameterKey=Subdomain,ParameterValue={subdomain}',
            f'ParameterKey=CertificateArn,ParameterValue={cert_arn if cert_arn else ""}',
            f'--profile', f'{profile}')
