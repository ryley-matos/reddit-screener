import praw
import boto3
import os
import time
import imgkit
import jinja2
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

bucket = boto3.resource('s3').Bucket('reddit-screener')

template_loader = jinja2.FileSystemLoader(searchpath="./templates/")
template_env = jinja2.Environment(loader=template_loader)

def get_praw_kwargs():
    praw_key_tups = [
        ('REDDIT_CLIENT_ID', 'client_id'),
        ('REDDIT_CLIENT_SECRET', 'client_secret'),
        ('REDDIT_PASSWORD', 'password')
    ]
    return {
        praw_key: os.environ[env_key] for (env_key, praw_key) in praw_key_tups
    }


reddit = praw.Reddit(
    **get_praw_kwargs(),
    user_agent='reddit-share',
    username='rylo-kin'
)


def wrap_html(content):
    template = template_env.get_template('comment_wrapper.html')
    return template.render(content=content)

def get_comment_html(node, children):
    username = node.author.name
    if (hasattr(node, 'parent_id')):
        children_html = f'<ul>{children}</ul>' if children else ''
        parent = reddit.comment(node.parent_id.replace('t1_', '')) if 't1_' in node.parent_id or 't3_' not in node.parent_id else reddit.submission(node.parent_id.replace('t3_', ''))
        template = template_env.get_template('comment.html')
        return get_comment_html(
            parent,
            template.render(username=username, comment_html=node.body_html, children_html=children_html)
        )
    else:
        template = template_env.get_template('submission.html')
        return wrap_html(
            template.render(title=node.title, username=username, children=children)
        )
def create_comment_image(comment):
    start = time.time()
    parent = reddit.comment(comment.parent_id.replace('t1_', '')) if 't1_' in comment.parent_id or 't3_' not in comment.parent_id else reddit.submission(comment.parent_id.replace('t3_', ''))
    img = imgkit.from_string(get_comment_html(parent, ''), False, options={'width': 750, 'disable-smart-width': ''})
    bucket.put_object(Key=f'{parent.id}.jpg', Body=img, ACL='public-read')
    end = time.time()
    comment.reply(f"Heres your screenshot: https://reddit-screener.s3.amazonaws.com/{parent.id}.jpg\nMade in {round(end - start, 2)} seconds")
