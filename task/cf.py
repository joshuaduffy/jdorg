from os import listdir
from invoke import task
from .commands import yarn, aws
from .util import chdir

WORKING_DIR = 'infra'


@task(help={
    "profile": "A valid AWS profile"
})
def validate(c, profile):
    with chdir(WORKING_DIR):
        for file in listdir():
            aws('cloudformation', 'validate-template',
                f'--template-body file://{file}',
                f'--profile {profile}')


@task(help={
    "stack_name": "The name to prefix before the stack.",
    "domain_name": "The domain name to configure. (e.g. joshuaduffy.org)",
    "profile": "A valid AWS profile."
})
def update_dns(c, stack_name, domain_name, profile, create=False):
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-dns',
            '--template-body file://zone.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile {profile}')

    aws('cloudformation', 'wait',
        f'stack-{action}-complete',
        f'--stack-name {stack_name}-dns',
        f'--profile {profile}')

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-dns-mail',
            '--template-body file://mail.yaml',
            f'--profile {profile}')


@task(help={
    "stack_name": "The name to prefix before the stack.",
    "domain_name": "The domain name to configure. (e.g. joshuaduffy.org)",
    "profile": "A valid AWS profile."
})
def update_cert(c, stack_name, domain_name, profile, create=False):
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-cert',
            '--template-body file://cert.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile {profile}')
        # Cert also needs adding to us-east-1 to be used by CloudFront
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-cert',
            '--template-body file://cert.yaml',
            '--parameters',
            f'ParameterKey=DomainName,ParameterValue={domain_name}',
            f'--profile {profile}',
            '--region us-east-1')


@task(help={
    "stack_name": "The name to prefix before the stack.",
    "subdomain": "The subdomain to configure. (e.g. www)",
    "cert_arn": "A valid certificate ARN.",
    "profile": "A valid AWS profile."
})
def update_client(c, stack_name, subdomain, cert_arn, profile, create=False):
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-client',
            '--template-body file://static-site.yaml',
            '--parameters',
            f'ParameterKey=Subdomain,ParameterValue={subdomain}',
            f'ParameterKey=CertificateArn,ParameterValue={cert_arn}',
            f'--profile {profile}')


@task(help={
    "stack_name": "The name to prefix before the stack.",
    "dns_name": "The DNS name you wish to alias to the TLD. (e.g. www.joshuaduffy.org)",
    "cert_arn": "A valid certificate ARN.",
    "profile": "A valid AWS profile."
})
def update_tld_redirect(c, stack_name, dns_name, cert_arn, profile, create=False):
    action = 'create' if create else 'update'

    with chdir(WORKING_DIR):
        aws('cloudformation', f'{action}-stack',
            f'--stack-name {stack_name}-dns-tld',
            '--template-body file://top-level-domain.yaml',
            '--parameters',
            f'ParameterKey=DNSName,ParameterValue={dns_name}',
            f'ParameterKey=CertificateArn,ParameterValue={cert_arn}',
            f'--profile {profile}')
