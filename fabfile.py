from fabric.api import *

def prepare():
    local('git add -p')
    local('git commit')
    local('git push')

def upload():
    local('rm -rf ./output/*')
    local('python generate.py')
    put('./output/*', '/srv/www/')

def deploy():
    prepare()
    upload()
