import json

import requests
from flask import Flask, request

import config
import utils

opt = config.auto_load_config()
app = Flask(__name__)


@app.route('/status', methods=['GET'])
def status():
    return 'OK'


@app.route('/notify', methods=['POST'])
def notify():
    file = request.files['file']
    plates = json.loads(request.form['plates'])
    jpg = file.read()
    url = f'https://api.telegram.org/bot{opt.bot.telegram_token}/sendPhoto'
    caption = utils.render_caption(plates, opt.bot.alert_color)
    files = {'photo': ('image.jpg', jpg, 'image/jpeg')}
    for cid in opt.bot.telegram_chat_id:
        data = {'chat_id': cid, 'caption': caption}
        resp = requests.post(url, files=files, data=data)
        print(resp.text)
    return 'OK'


if __name__ == '__main__':
    app.run(host=opt.notify.host, port=opt.notify.port)
