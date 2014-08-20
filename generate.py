#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader, evalcontextfilter, Markup
from PIL import Image
import subprocess
import os, glob, shutil
import yaml
import datetime
from pprint import pprint
import markdown2
import os, errno

# A quick and dirty static site generator (kind of like Jekyll) to generate
# static HTML for my personal site. Warning: this code is messy and not
# for public consumption :)
#
# This code is public domain, should anyone want to attempt to repurpose it.
# (I retain copyright of all content and the design of the site, except as
# otherwise noted.)

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

markdown_renderer = markdown2.Markdown(extras=[
    'fenced-code-blocks',
    'smarty-pants'
])

@evalcontextfilter
def render_markdown2(eval_ctx, value):
    extensions = [
        'fenced_code',
        'codehilite'
    ]
    if eval_ctx.autoescape:
        return Markup(markdown_renderer.convert(value))
    else:
        return markdown_renderer.convert(value)

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
OUTPUT_ROOT = os.path.join(APP_ROOT, 'output')

env = Environment(loader=FileSystemLoader(
    os.path.join(APP_ROOT, 'templates')
))
env.filters['markdown'] = render_markdown2

# refresh static files
subprocess.call('cp -Rpv {src} {dst}'.format(
    src=os.path.join(APP_ROOT, 'static', '*'),
    dst=os.path.join(APP_ROOT, 'output')), shell=True)

portfolio = {}
project_template = env.get_template('project.html')

# Parse available portfolio projects
for project in glob.glob(os.path.join(APP_ROOT, 'portfolio', '*', 'project.yml')):
    project_dir = os.path.split(project)[0]
    project_name = os.path.split(project_dir)[1] # directory base name
    print 'Found project {0} ({1})'.format(project_name, project)
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
        thumbdest = os.path.join(thumbs_dir, image['filename'])
        defaultdest = os.path.join(OUTPUT_ROOT, project_name, image['filename'])

        if os.path.exists(thumbdest) and os.path.exists(defaultdest):
            continue # don't regenerate if output files exist

        im = Image.open(os.path.join(project_dir, image['filename']))
        thumb = im.copy()
        default = im.copy()

        thumb.thumbnail(thumb_size, Image.ANTIALIAS)
        thumb.save(thumbdest)

        default.thumbnail(default_size, Image.ANTIALIAS)
        default.save(defaultdest)

        subprocess.call('cp -pv {src} {dst}'.format(
            src=os.path.join(project_dir, image['filename']),
            dst=fullsize_dir,
        ), shell=True)

all_posts = []
post_template = env.get_template('post.html')
# parse available blog posts
for post_path in glob.glob(os.path.join(APP_ROOT, 'posts', '*.md')):
    post_filename = os.path.split(post_path)[1]
    y, m, d = map(int, post_filename.split('-')[:3])
    post_date = datetime.date(y, m, d)
    post_slug = '-'.join(post_filename.split('-')[3:])[:-3] # chop off '.md'

    print 'Found blog post', post_slug

    post_data = open(post_path, 'r').read()
    post_meta, post_content = post_data.split('---', 2)[1:]
    post = yaml.load(post_meta.strip())
    post['content'] = post_content.strip()
    post['date'] = post_date
    post['slug'] = post_slug

    # generate individual post files
    ensure_dir(os.path.join(OUTPUT_ROOT, 'writing', post_slug))
    with open(os.path.join(OUTPUT_ROOT,  'writing', post_slug, 'index.html'), 'w') as f:
        f.write(post_template.render(**post))

    # copy supporting files for post
    if os.path.isdir(post_path[:-3]): # chop off .md and check if there's a directory
        for post_file in glob.glob(os.path.join(APP_ROOT, 'posts', post_path[:-3], '*')):
            # print post_file, '->', os.path.join(APP_ROOT, 'output', 'writing', post_slug, post_file)
            subprocess.call('cp -Rp {src} {dst}'.format(
                src=post_file,
                dst=os.path.join(APP_ROOT, 'output', 'writing', post_slug)), shell=True)

    all_posts.append((post_date, post))

# sort and generate post archive
all_posts.sort()
all_posts.reverse()
all_posts = [
    post[1] for post in all_posts
    if not post[1].get('draft')
]
archive_template = env.get_template('archive.html')

ensure_dir(os.path.join(OUTPUT_ROOT, 'writing'))
with open(os.path.join(OUTPUT_ROOT,  'writing', 'index.html'), 'w') as f:
    f.write(archive_template.render(posts=all_posts))

# generate homepage
home_template = env.get_template("home.html")

# sort the processed projects
projects = [(info['datestamp'], key) for key, info in portfolio.items()]
projects.sort()
projects.reverse()

sorted_portfolio = [(key, portfolio[key]) for date, key in projects]

# load and sort positions

positions = []

for position_file in glob.glob(os.path.join(APP_ROOT, 'experience', '*.yml')):
    with open(position_file) as f:
        position = yaml.safe_load(f)
    positions.append((position['datestamp'], position))

positions.sort()
positions.reverse()
positions = [data for datestamp, data in positions if datestamp < datetime.date.today()]

# render the homepage

with open(os.path.join(OUTPUT_ROOT, 'index.html'), 'w') as f:
    f.write(home_template.render(
        projects=sorted_portfolio,
        positions=positions,
        posts=all_posts[:10]
    ))
