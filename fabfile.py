# -*- coding: utf-8 -*-
import os
import sys
import posixpath

from fabric.api import env, local, run, sudo, put, cd, runs_once, prompt, require, settings
from fabric.contrib.files import exists, upload_template
from fabric.contrib.console import confirm
from fabric.context_managers import hide

#from fabfile_nginx import get_django_grappelli_from_svn

# Global settings
env.project_name = 'munin_exchange' # Project name
env.project_domain = 'exchange.munin-monitoring.org' # Project domain
env.project_directory = '' # Local project working directory

# Environments
def production():
  "Production environment"

  # General settings
  env.hosts = [''] # One or multiple server addresses in format ip:port
  env.path = '' # Path where your application will be deployed
  env.user = '' # Username used when making SSH connections
  env.www_user = '' # User account under which Nginx is running
  env.ftp_user = ''
  env.ftp_group = ''
  env.password = '' # Connection and sudo password (you can omit it and Fabric will prompt you when necessary)
  env.key_filename = ['']
  env.shell = '/usr/local/bin/bash -l -c' # Path to your shell binary
  env.sudo_prompt = 'Password:' # Sudo password prompt
  env.redis_db = 1

  # Database settings
  env.db_hostname = 'localhost'
  env.db_username = ''
  env.db_password = ''
  env.db_name = ''
  env.db_file = 'db_dump.sql'

# Tasks
def run_tests():
  "Run the test suite"

  local('python %(project_name)s/manage.py test' % {'project_name': env.project_name})

def get_django_from_svn():
  "Download the latest Django release from SVN"
  require('path')

  run('cd %(path)s; svn co http://code.djangoproject.com/svn/django/trunk/ django-trunk' % {'path': env.path})
  run('ln -s -f %(path)s/django-trunk/django %(path)s/lib/python2.6/site-packages/django' % {'path': env.path})

def get_django_grappelli_from_svn():
  "Download the latest django-grappelli from SVN"
  require('path')

  run('cd %(path)s; svn co http://django-grappelli.googlecode.com/svn/trunk/grappelli django-grappelli-trunk' % {'path': env.path})
  run('ln -s -f %(path)s/django-grappelli-trunk %(path)s/lib/python2.6/site-packages/grappelli' % {'path': env.path})

def update_django_from_svn():
  "Update the local Django SVN release"
  require('path')

  run('cd %(path)s/django-trunk; svn update' % {'path': env.path})

def setup():
  "Create a new Python virtual environment and folders where our application will be saved"
  require('hosts', provided_by = [production])
  require('path')

def flush_redis_cache():
  "Flush Redis database."
  require('hosts', provided_by = [production])

  pass

def deploy_site():
  """
  Deploy the latest version of the site to the server(s), install any
  required third party modules, install the virtual hosts and
  then reload the Apache and lighttpd
  """
  require('hosts', provided_by = [production])
  require('path')

  import time
  env.release = time.strftime('%Y%m%d%H%M%S')
  env.version = _get_latest_git_tag()

  _upload_archive_from_git()

  with settings(warn_only=True):
    _maintenance_up()

#  _install_dependencies()
  _install_site()
  _symlink_uploads_directory()
  _symlink_current_release()
  _symlink_grappeli_media()
  _create_database_schema()
#  _load_fixtures()
  _reload_apache()
  _reload_nginx()

def _update_version_number():
  require('hosts', provided_by = [production])
  require('path')

  run('''sed -i -e "s/<span class="version">.*<\/span>/<span class="version">%(version)s<\/span>/g" sgrstats/templates/header.html'''  % {'version': env.version.replace(r'.', r'\.')})

def deploy_database():
  """
  Deploy the database (import data located in db_file)
  """
  require('db_hostname', 'db_username', 'db_password', 'db_name', 'db_file')
  require('release', provided_by = [deploy_site, setup])

  run('mysql -h %(db_hostname)s -u %(db_username)s -p%(db_password)s %(db_name)s < %(path)s/releases/%(release)s/other/%(db_file)s' % {'path': env.path, 'release': env.release, 'db_hostname': env.db_hostname, 'db_username': env.db_username, 'db_password': env.db_password, 'db_name': env.db_name, 'db_file': env.db_file})
  run('rm %(path)s/releases/%(release)s/other/%(db_file)s' % {'path': env.path, 'release': env.release, 'db_file': env.db_file})

def deploy_release(release):
  "Specify a specific release to be made live"
  require('hosts', provided_by = [production])
  require('path')

  env.release = release
  run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;'  % {'path': env.path})
  run('cd %(path)s; ln -s -f %(release)s releases/current'  % {'path': env.path, 'release': env.release})

  _reload_apache()

def rollback():
  """
  Limited rollback capability. Simple loads the previously current
  version of the code. Rolling back again will swap between the two.
  """
  require('hosts', provided_by = [production])
  require('path')

  run('cd %(path)s; mv releases/current releases/_previous;' % {'path': env.path})
  run('cd %(path)s; mv releases/previous releases/current;' % {'path': env.path})
  run('cd %(path)s; mv releases/_previous releases/previous;' % {'path': env.path})

  _reload_apache()

def upgrade_packages():
  pass

def cleanup():
  """
  Clean up the remote environment.
  Flush the database, delete the Apache and lighttpd vhosts, uninstall
  installed dependencies and remove everything from directory packages, releases and other
  """

  with settings(hide('warnings', 'stderr', 'stdout'), warn_only = True):
    # Flush the database
    #run('cd %(path)s/releases/current/%(project_name)s; ../../../bin/python manage.py flush --noinput' % {'path': env.path, 'project_name': env.project_name})

    # Delete the Apache and lighttpd vhost config files
    sudo('rm /usr/local/etc/apache22/sites-available/%(project_domain)s.conf'  % {'project_domain': env.project_domain})
    sudo('rm /usr/local/etc/apache22/sites-enabled/%(project_domain)s.conf' % {'project_domain': env.project_domain})
    sudo('rm /usr/local/etc/lighttpd/%(project_domain)s.conf' % {'project_domain': env.project_domain})

    # Remove the include statement from the lighttpd config file for our vhost
    sudo('sed \'/\/usr\/local\/etc\/lighttpd\/%(project_domain)s.conf/d\' /usr/local/etc/lighttpd.conf > /usr/local/etc/lighttpd.conf.1; mv /usr/local/etc/lighttpd.conf.1 /usr/local/etc/lighttpd.conf' % {'project_domain': env.project_domain})

    # Uninstall installed dependencies
    run('cd %(path)s; pip uninstall -E . -r ./releases/current/requirements.txt -y' % {'path': env.path})

    # Remove directory packages, releases and other (if exists)
    sudo('rm -rf %(path)s/packages/'  % {'path': env.path})
    sudo('rm -rf %(path)s/releases/' % {'path': env.path})

    _reload_apache()
    _reload_lighttpd()

# Helpers - these are called by other functions rather than directly
def _get_latest_git_tag():
  """Return the git tag of the latest commit"""
  last_commit = local('git rev-list HEAD --max-count=1').split('\n')[0]
  last_tag = local('git tag --contains %(last_commit)s' % {'last_commit': last_commit}).split('\n')[0]

  return last_tag

def _upload_archive_from_git():
  "Create an archive from the current Git master branch and upload it"
  require('release', provided_by = [deploy_site, setup])

  local('git archive --format=zip master > %(release)s.zip' % {'release': env.release})
  run('mkdir %(path)s/releases/%(release)s' % {'path': env.path, 'release': env.release})
  put('%(release)s.zip' % {'release': env.release}, '%(path)s/packages/' % {'path': env.path})
  run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.zip' % {'path': env.path, 'release': env.release})
  local('rm %(release)s.zip' % {'release': env.release})

def _maintenance_up():
  """
  Install the Apache maintenance configuration.
  """
  require('release', provided_by = [deploy_site, setup])

  sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s/configs/production/apache_maintenance /usr/local/etc/apache22/sites-available/%(project_domain)s.conf' % {'path': env.path, 'release': env.release, 'project_name': env.project_name, 'project_domain': env.project_domain})
  sudo('ln -s -f /usr/local/etc/apache22/sites-available/%(project_domain)s.conf /usr/local/etc/apache22/sites-enabled/%(project_domain)s.conf' % {'project_domain': env.project_domain, 'project_name': env.project_name})
  _reload_apache()

def _install_site():
  "Add the virtualhost to Apache and lighttpd and move the production settings config file"
  require('release', provided_by = [deploy_site, setup])

  # Apache
  sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s/configs/production/apache /usr/local/etc/apache22/sites-available/%(project_domain)s.conf' % {'path': env.path, 'release': env.release, 'project_name': env.project_name, 'project_domain': env.project_domain})
  sudo('ln -s -f /usr/local/etc/apache22/sites-available/%(project_domain)s.conf /usr/local/etc/apache22/sites-enabled/%(project_domain)s.conf' % {'project_domain': env.project_domain, 'project_name': env.project_name})

  # nginx
  sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s/configs/production/nginx /usr/local/etc/nginx/sites-available/%(project_domain)s.conf' % {'path': env.path, 'release': env.release, 'project_name': env.project_name, 'project_domain': env.project_domain})
  sudo('ln -s -f /usr/local/etc/nginx/sites-available/%(project_domain)s.conf /usr/local/etc/nginx/sites-enabled/%(project_domain)s.conf' % {'project_domain': env.project_domain, 'project_name': env.project_name})

  # Change permissions
  run('cd %(path)s/releases/%(release)s; rm -rf other/' % {'path': env.path, 'release': env.release})
  sudo('chown -R %(www_user)s:%(www_user)s %(path)s/releases/%(release)s' % {'www_user': env.www_user, 'path': env.path, 'release': env.release})

def _compress_images():
  "Compress images"
  require('release', provided_by = [deploy_site, setup])
  run('python /usr/local/bin/asset_deflator.py --path=%(path)s/releases/%(release)s/static/site_media/ --overwrite --compress-images' % {'path': env.path, 'release': env.release})

def _install_dependencies():
  "Install the required packages from the requirements file using PIP"
  require('release', provided_by = [deploy_site, setup])

  with settings(warn_only = True):
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' % {'path': env.path, 'release': env.release})

def _symlink_current_release():
  "Symlink our current release"
  require('release', provided_by = [deploy_site, setup])

  # Don't print warrnings if there is no current release
  with settings(hide('warnings', 'stderr'), warn_only = True):
    run('cd %(path)s; rm releases/previous; mv releases/current releases/previous' % {'path': env.path})

  run('cd %(path)s; ln -s -f %(release)s releases/current' % {'path': env.path, 'release': env.release})

def _symlink_uploads_directory():
  "Create symbolic link for uploads directory in static/site_media/images"
  require('release', provided_by = [deploy_site, setup])

  # Don't print warrnings if there is no current release
  with settings(hide('warnings', 'stderr'), warn_only = True):
    run('ln -s -f %(path)s/uploads %(path)s/releases/%(release)s/static/site_media/images/uploads' % {'path': env.path, 'release': env.release})
    run('ln -s -f %(path)s/uploads/plugins %(path)s/releases/%(release)s/munin_exchange/assets/site_media/plugins' % {'path': env.path, 'release': env.release})
    run('ln -s -f %(path)s/uploads/screenshots %(path)s/releases/%(release)s/munin_exchange/assets/site_media/images/plugins' % {'path': env.path, 'release': env.release})

def _symlink_django_admin_media():
  require('hosts', provided_by = [production])
  require('path')
  run('ln -s %(path)s/src/django/django/contrib/admin/media/ %(path)s/releases/current/munin_exchange/assets/admin_media' % {'path': env.path})

def _symlink_grappeli_media():
  require('hosts', provided_by = [production])
  require('path')
  run('ln -s %(path)s/src/grappelli/grappelli/media %(path)s/releases/current/munin_exchange/assets/admin_media' % {'path': env.path})

def _create_database_schema():
  "Create the database tables for all apps in INSTALLED_APPS whose tables have not already been created"
  require('project_name')

  run('cd %(path)s/releases/current/%(project_name)s; ../../../bin/python configs/production/manage.py syncdb --noinput' % {'path': env.path, 'project_name': env.project_name})

def _load_fixtures():
  """ Loads project's initial fixtures. """
  require('project_name')

  run('cd %(path)s/releases/current/%(project_name)s; ../../../bin/python configs/production/manage.py loaddata ../data/fixtures/munin_exchange_import.json' % {'path': env.path, 'project_name': env.project_name})

def _reload_apache():
  "Reload the apache server"
  sudo('/usr/local/etc/rc.d/apache22 reload')

def _reload_lighttpd():
  "Reload the lighttpd server"
  sudo('/usr/local/etc/rc.d/lighttpd reload')

def _reload_nginx():
  "Reload the nginx server"
  sudo('/usr/local/etc/rc.d/nginx reload')
