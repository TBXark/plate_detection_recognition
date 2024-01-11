import json
import os
from threading import Thread

import cv2
import numpy as np
import requests
from flask import Flask, Response

import config
from recognition import Recognition

opt = config.auto_load_config()
app = Flask(__name__)
files = os.listdir('./imgs')
file_index = 0
current_file = None


def reload_latest_image():
    global current_file, file_index
    while True:
        with open('./imgs/' + files[file_index], 'rb') as f:
            jpg = f.read()
        current_file = jpg
        file_index = (file_index + 1) % len(files)


def get_latest_frame():
    global current_file
    if current_file is None:
        return None, None
    frame = cv2.imdecode(np.frombuffer(current_file, np.uint8), cv2.IMREAD_COLOR)
    return frame, current_file


def send_notify_callback(plates, jpg):
    files = {'file': ('image.jpg', jpg, 'image/jpeg')}
    data = {'plates': json.dumps(plates)}
    requests.post(opt.camera.notify_api, files=files, data=data)


@app.route('/latest_frame', methods=['GET'])
def latest_frame_route():
    global current_file
    return Response(current_file, mimetype='image/jpeg')


if __name__ == '__main__':

    Thread(target=reload_latest_image, name='camera', daemon=True).start()

    if opt.rec.auto_recognition:
        rec = Recognition(opt.rec)
        Thread(target=rec.start, args=(get_latest_frame, send_notify_callback), name='recognition', daemon=True).start()

    app.run(host="localhost", port=5000)
