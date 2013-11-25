from jinja2 import Environment, FileSystemLoader, evalcontextfilter, Markup
from PIL import Image
import subprocess
import os, glob, shutil
import yaml
from pprint import pprint
from markdown import markdown

import os, errno

def ensure_dir(path):
    """
    Creates the directory given by path unless it already exists
    """
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    return path

@evalcontextfilter
def render_markdown(eval_ctx, value):
    if eval_ctx.autoescape:
        return Markup(markdown(value))
    else:
        return markdown(value)

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
OUTPUT_ROOT = os.path.join(APP_ROOT, 'output')

env = Environment(loader=FileSystemLoader(
    os.path.join(APP_ROOT, 'templates')
))
env.filters['markdown'] = render_markdown

# refresh static files
subprocess.call('cp -Rpv {src} {dst}'.format(
    src=os.path.join(APP_ROOT, 'static', '*'),
    dst=os.path.join(APP_ROOT, 'output')), shell=True)

portfolio = {}
project_template = env.get_template('project.html')

# Parse available portfolio projects
for project in glob.glob(os.path.join(APP_ROOT, 'portfolio', '*', 'project.yml')):
    print 'Found project: {0}'.format(project)
    project_dir = os.path.split(project)[0]
    project_name = os.path.split(project_dir)[1] # directory base name
    with open(project) as f:
        portfolio[project_name] = yaml.safe_load(f)
        # YAML turns a double linebreak into a single one, breaking Markdown
        portfolio[project_name]['description'] = portfolio[project_name]['description'].replace('\n', '\n\n')
    
    # generate portfolio pages
    ensure_dir(os.path.join(OUTPUT_ROOT, project_name))
    with open(os.path.join(OUTPUT_ROOT, project_name, 'index.html'), 'w') as f:
        f.write(project_template.render(**portfolio[project_name]))
    
    if os.path.exists(os.path.join(project_dir, 'thumb.png')):
        shutil.copy2(
            os.path.join(project_dir, 'thumb.png'),
            os.path.join(OUTPUT_ROOT, project_name)
        )
        portfolio[project_name]['thumb'] = 'thumb.png'
    
    # generate resized images
    thumb_size = 150, 150
    thumbs_dir = os.path.join(OUTPUT_ROOT, project_name, 'thumbs')
    ensure_dir(thumbs_dir)
    
    default_size = 460, 460
    
    fullsize_dir = os.path.join(OUTPUT_ROOT, project_name, 'full')
    ensure_dir(fullsize_dir)
    
    for image in portfolio[project_name]['images']:
        im = Image.open(os.path.join(project_dir, image['filename']))
        thumb = im.copy()
        default = im.copy()
        
        thumb.thumbnail(thumb_size, Image.ANTIALIAS)
        thumb.save(os.path.join(thumbs_dir, image['filename']))
        
        default.thumbnail(default_size, Image.ANTIALIAS)
        default.save(os.path.join(OUTPUT_ROOT, project_name, image['filename']))
        
        subprocess.call('cp -pv {src} {dst}'.format(
            src=os.path.join(project_dir, image['filename']),
            dst=fullsize_dir,
        ), shell=True)
    
# generate homepage

projects = [(info['datestamp'], key) for key, info in portfolio.items()]
projects.sort()
projects.reverse()

sorted_portfolio = [(key, portfolio[key]) for date, key in projects]
pprint(sorted_portfolio)

home_template = env.get_template("home.html")

positions = []

for position_file in glob.glob(os.path.join(APP_ROOT, 'experience', '*.yml')):
    with open(position_file) as f:
        position = yaml.safe_load(f)
    positions.append((position['datestamp'], position))

positions.sort()
positions.reverse()
positions = [data for datestamp, data in positions]

with open(os.path.join(OUTPUT_ROOT, 'index.html'), 'w') as f:
    f.write(home_template.render(
        projects=sorted_portfolio,
        positions=positions
    ))
