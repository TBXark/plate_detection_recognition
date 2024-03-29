import json
from threading import Thread
from typing import Union

import cv2
import requests
from flask import Flask, Response

import config
from recognition import Recognition, ImageWrapper

opt = config.auto_load_config()
app = Flask(__name__)
latest_frame: Union[None, cv2.typing.MatLike] = None


def reload_latest_frame():
    global latest_frame
    cap = cv2.VideoCapture(opt.camera.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    while True:
        ret, frame = cap.read()
        if ret is not None:
            latest_frame = frame
    # cap.release()


def get_latest_frame():
    global latest_frame
    if latest_frame is None:
        return None
    return ImageWrapper(frame=latest_frame, jpg=None)


def send_notify_callback(plates, jpg):
    files = {'file': ('image.jpg', jpg, 'image/jpeg')}
    data = {'plates': json.dumps(plates)}
    requests.post(opt.camera.notify_api, files=files, data=data)


@app.route('/status', methods=['GET'])
def status():
    return 'OK'


@app.route('/latest_frame', methods=['GET'])
def latest_frame_route():
    raw = get_latest_frame()
    if raw is None:
        return Response(None, mimetype='image/jpeg')
    jpg = raw.toJPEG()
    return Response(jpg, mimetype='image/jpeg')


if __name__ == '__main__':

    Thread(target=reload_latest_frame, name='camera', daemon=True).start()

    if opt.rec.auto_recognition:
        rec = Recognition(opt.rec)
        Thread(target=rec.start, args=(get_latest_frame, send_notify_callback), name='rec', daemon=True).start()

    app.run(host=opt.camera.host, port=opt.camera.port)
