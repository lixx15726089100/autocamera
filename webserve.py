# coding:utf-8
from flask import Flask, render_template, url_for
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Flask RUN on Rsapberry2B!'


@app.route('/gallery')
def my_gallery():
    # 构建一个双重列表，并排好顺序
    os.chdir('/home/pi/pyprj/cannon5dcaptureandmail/')
    dirs = os.listdir('static')
    dirs.sort()
    dirs.reverse()

    items = {}
    for dir in dirs:
        filenames = os.listdir('static/' + dir)
        filenames.sort()
        items[dir] = filenames

    return render_template('index.html', items=items)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
