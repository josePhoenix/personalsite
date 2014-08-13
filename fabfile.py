from fabric.api import *
import unicodedata
import re
import datetime
import os.path

env.hosts = ['joseph-long.com']

def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value)
    return re.sub('[-\s]+', '-', value).strip().lower()

def prepare():
    local('git add -p')
    with settings(warn_only=True):
        local('git commit')
    local('git push')

def upload():
    local('rm -rf ./output/*')
    local('python generate.py')
    local('rsync -avz --no-t --no-p -e ssh ./output/ josephoenix@joseph-long.com:"~/www/"')

def deploy():
    prepare()
    upload()

def post():
    slug_title = unicode(prompt("What is the short title for the post?"))
    slug = slugify(slug_title)
    full_slug = '{0}-{1}'.format(datetime.date.today().isoformat(), slug)
    local('cp ./skeletons/post.md ./posts/{0}.md'.format(full_slug))
    local('mkdir ./posts/{0}/'.format(full_slug))

def portfolio():
    slug_title = unicode(prompt("What's an unambiguous short name for this project?"))
    slug = slugify(slug_title)
    local('mkdir ./portfolio/{0}'.format(slug))
    local('cp ./skeletons/portfolio.yml ./portfolio/{0}/project.yml'.format(slug))

def experience():
    slug_title = unicode(prompt("What's an unambiguous short name for this employer?"))
    slug = slugify(slug_title)
    local('cp ./skeletons/experience.yml ./experience/{0}.yml'.format(slug))

def page():
    slug_title = unicode(prompt("What's an unambiguous short name for this page?"))
    slug = slugify(slug_title)
    target = './pages/{0}.md'.format(slug)
    if os.path.isfile(target):
        raise RuntimeError("Destination file {0} exists already!".format(target))
    local('cp ./skeletons/page.md {0}'.format(target))
