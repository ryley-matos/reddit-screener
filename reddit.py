import praw
import boto3
import os
import time
import imgkit
from dotenv import load_dotenv

load_dotenv()

bucket = boto3.resource('s3').Bucket('reddit-screener')

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
    return """
        <html>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
            <style>
                ul {
                    border-left: 2px solid green;
                    list-style-type: none;
                    padding-inline-start: 1em;
                }

                body {
                    max-width: 750px;
                    font-family: 'Roboto', sans-serif;
                }
            </style>
            <body>
                %s
            </body>
        </html>
    """ % content

def get_comment_html(node, children):
    if (hasattr(node, 'parent_id')):
        return get_comment_html(
            reddit.comment(node.parent_id.replace('t1_', '')) if 't1_' in node.parent_id or 't3_' not in node.parent_id else reddit.submission(node.parent_id.replace('t3_', '')),
            f"<li>{node.body_html}<ul>{children}</ul></li>" if children else f"<li>{node.body_html}</li>"
        )
    else:
        return wrap_html("""<ul><li><h3>%s</h3><ul>%s</ul></li></ul>""" % (node.title, children))

def create_comment_image(comment):
    start = time.time()
    parent = reddit.comment(comment.parent_id.replace('t1_', '')) if 't1_' in comment.parent_id or 't3_' not in comment.parent_id else reddit.submission(comment.parent_id.replace('t3_', ''))
    img = imgkit.from_string(get_comment_html(parent, ''), False, options={'width': 750, 'disable-smart-width': ''})
    bucket.put_object(Key=f'{parent.id}.jpg', Body=img, ACL='public-read')
    end = time.time()
    comment.reply(f"Heres your screenshot: https://reddit-screener.s3.amazonaws.com/{parent.id}.jpg\nMade in {round(end - start, 2)} seconds")
