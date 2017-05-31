# Includes AWS fixes from:
# https://stackoverflow.com/questions/5327465/using-an-ssh-keyfile-with-fabric


from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random


REPO_URL = 'https://github.com/sametz/tdd2e_aws.git'
env.user = 'ubuntu'
# Had to move .pem to another folder because "Google Drive" space in name
# causes "no such file or directory error" when script run!
env.key_filename = '~/Documents/aws/thompetz_aws.pem'
env.hosts = ["ec2-52-14-249-213.us-east-2.compute.amazonaws.com"]
#env.hosts = ["52.14.249.213"]

#print('env.port = :', env.port)
# print('env.roledefs:')
# print(env.roledefs)


def deploy():
    print('env.user: ', env.user)
    print('env.host: ', env.host)
    site_folder = f'/home/{env.user}/sites/{env.host}'
    print('site folder: ', site_folder)
    source_folder = site_folder + '/source'

    # Functions from SO answer on AWS
    local_uname()
    remote_uname()

    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def local_uname():
    local('uname -a')


def remote_uname():
    run('uname -a')


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    current_commit = local("git log -n l --format=%H", capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        f'ALLOWED_HOSTS = ["{site_name}"]'
        )
    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"')
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3.6 -m venv {virtualenv_folder}')
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')


def _update_static_files(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    )


def _update_database(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py migrate --noinput'
    )