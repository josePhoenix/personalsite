from fabric.api import *
import unicodedata
import re
import datetime
import os
import os.path
import glob

env.hosts = ['joseph-long.com']

def _slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value)
    return re.sub('[-\s]+', '-', value).strip().lower()

def _replace_in_file(original, replacement, filename):
    with open(filename + '.tmp', 'w') as f, open(filename) as forig:
        for line in forig:
            f.write(line.replace(original, replacement))
    os.rename(filename + '.tmp', filename)

def _markdown_add_code_fences(filename):
    with open(filename + '.tmp', 'w') as f, open(filename) as forig:
        in_code_block = False
        # enter code block on a line starting with 4 spaces
        # exit code block on a blank line
        for line in forig:
            if line[:4] == '    ':
                if not in_code_block:
                    in_code_block = True
                    f.write('```python\n')
                line = line[4:]
            else:
                if in_code_block:
                    in_code_block = False
                    f.write('```\n')
            f.write(line)
    os.rename(filename + '.tmp', filename)

def prepare():
    local('git add -p')
    with settings(warn_only=True):
        local('git commit')
    local('git push')
    build()

def build():
    local('rm -rf ./output/*')
    local('python generate.py')

def upload():
    local('rsync -avz --no-t --no-p -e ssh ./output/ josephoenix@joseph-long.com:"~/www/"')

def deploy():
    prepare()
    upload()

def post():
    slug_title = unicode(prompt("What is the short title for the post?"))
    slug = _slugify(slug_title)
    full_slug = '{0}-{1}'.format(datetime.date.today().isoformat(), slug)
    local('cp ./skeletons/post.md ./posts/{0}.md'.format(full_slug))
    local('mkdir ./posts/{0}/'.format(full_slug))

def portfolio():
    slug_title = unicode(prompt("What's an unambiguous short name for this project?"))
    slug = _slugify(slug_title)
    local('mkdir ./portfolio/{0}'.format(slug))
    local('cp ./skeletons/portfolio.yml ./portfolio/{0}/project.yml'.format(slug))

def experience():
    slug_title = unicode(prompt("What's an unambiguous short name for this employer?"))
    slug = _slugify(slug_title)
    local('cp ./skeletons/experience.yml ./experience/{0}.yml'.format(slug))

def page():
    slug_title = unicode(prompt("What's an unambiguous short name for this page?"))
    slug = _slugify(slug_title)
    target = './pages/{0}.md'.format(slug)
    if os.path.isfile(target):
        raise RuntimeError("Destination file {0} exists already!".format(target))
    local('cp ./skeletons/page.md {0}'.format(target))

def notebook(nbfilename):
    if not os.path.exists('./notebooks/{}'.format(nbfilename)):
        raise RuntimeError("No notebook named {} found!".format(nbfilename))
    slug_title = unicode(prompt("What's an unambiguous short name for this post?"))
    slug = _slugify(slug_title)
    full_slug = '{0}-{1}'.format(datetime.date.today().isoformat(), slug)
    target = './posts/{0}.md'.format(full_slug)
    if os.path.isfile(target):
        raise RuntimeError("Destination file {0} exists already!".format(target))
    local('mkdir ./posts/{0}/'.format(full_slug))
    with lcd("./notebooks/"):
        local('ipython nbconvert --to markdown {}'.format(nbfilename))
    local("cp -v ./notebooks/{}/*.png ./posts/{}/".format(nbfilename.replace('.ipynb', '_files'), full_slug))
    post_skel = open('./skeletons/post.md').read()
    preamble, _ = post_skel.rsplit('---', 1)
    with open(target, 'w') as f:
        f.write(preamble)
        f.write('---\n')
    local("cat ./notebooks/{} >> {}".format(nbfilename.replace('.ipynb', '.md'), target))
    
    # post-process the notebook markdown
    _replace_in_file(nbfilename.replace('.ipynb', '_files') + '/', '', target)
    _markdown_add_code_fences(target)
