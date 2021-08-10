import imgkit
import boto3
from reddit import reddit, create_comment_image
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    print('listening..')
    all_reddit = reddit.subreddit("all")
    for comment in all_reddit.stream.comments():
        if ('!Screenshot' in comment.body):
            print('comment found!')
            create_comment_image(comment)
            

