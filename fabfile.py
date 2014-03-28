from fabric.api import *

def prepare():
    local('git add -p && git commit')
    local('git push')

def upload():
    put('./output/*', '/srv/www/')

def deploy():
    prepare()
    upload()
