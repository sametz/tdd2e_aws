from fabric.api import env, run
from fabric.context_managers import settings

# OTTG answer to my Q in Ch21: fix to get around AWS ubuntu password request
env.key_filename = ["~/Documents/aws/thompetz_aws.pem"]


def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py'


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'ubuntu@{host}'):
        # TDD version (line below) required ubuntu password, not available
        # on standard AWS EC2
        run(f'{manage_dot_py} flush --noinput')


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'ubuntu@{host}'):
        session_key = run(f'{manage_dot_py} create_session {email}')
        return session_key.strip()