from fabric.api import *

def prepare():
    local('git add -p && git commit')
    local('git push')

def deploy():
    prepare()
    put('./output/*', '/srv/www/')
