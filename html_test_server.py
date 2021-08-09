from flask import Flask
from reddit import reddit, get_comment_html

app = Flask(__name__)

TEST_ID = 'h8arrkx'

@app.route('/')
def test():
    comment = reddit.comment(TEST_ID)
    return get_comment_html(comment, '')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
