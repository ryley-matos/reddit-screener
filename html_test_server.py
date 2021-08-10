from flask import Flask
from reddit import reddit, get_comment_html
import imgkit

app = Flask(__name__)

TEST_ID = 'h8arrkx'

@app.route('/')
def test():
    comment = reddit.comment(TEST_ID)
    html = get_comment_html(comment, '')
    imgkit.from_string(html, 'out.jpg', options={'width': 600})
    return html 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    

