import cv2
import time

from onnx import load_onnx_model, rec_by_session


class ImageWrapper:
    def __init__(self, frame, jpg):
        if frame is not None and frame.shape[-1] == 4:
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        else:
            self.frame = frame
        # 判断 jpg 是 bytes
        if jpg is not None and isinstance(jpg, bytes):
            self.jpg = jpg

    def toJPEG(self):
        if self.jpg is None:
            self.jpg = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 60])[1].tobytes()
        return self.jpg

    def toFrame(self):
        if self.frame is None:
            frame = cv2.imdecode(self.jpg, cv2.IMREAD_COLOR)
            if frame.shape[-1] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            self.frame = frame
        return self.frame


class Recognition:
    def __init__(self, _opt):
        session_detect, session_rec = load_onnx_model(_opt.detect_model, _opt.rec_model)
        img_size = (_opt.img_size, _opt.img_size)

        def detect(image):
            start_time = time.time()
            result = rec_by_session(image, img_size, session_detect, session_rec)
            print('recognition time: ', time.time() - start_time)
            return result

        self.detect = detect

    def get_plates(self, image):
        result = self.detect(image)
        if len(result) > 0:
            plate_list = []
            for i, r in enumerate(result):
                plate = {'no': r['plate_no'], 'color': r['plate_color']}
                plate_list.append(plate)
            return plate_list
        else:
            return None

    def start(self, fetch_image, callback):
        print('start plate recognition')
        last_rec_plates = {}
        while True:
            try:
                img_obj = fetch_image()
                if img_obj is None:
                    continue
                frame = img_obj.toFrame()
                if frame is None:
                    continue
                result = self.get_plates(frame)
                can_send = True
                if result is not None and len(result) > 0:
                    # 如果last_rec_plates中不存在或者存在时间超过30秒，就发送
                    for p in result:
                        if p['no'] not in last_rec_plates:
                            last_rec_plates[p['no']] = time.time()
                        else:
                            if time.time() - last_rec_plates[p['no']] > 30:
                                last_rec_plates[p['no']] = time.time()
                            else:
                                can_send = False
                                continue
                    if not can_send:
                        continue
                    callback(result, img_obj.toJPEG())
            except Exception as e:
                print(e)


if __name__ == '__main__':
    import os
    from config import RecognitionOpt

    opt = RecognitionOpt({
        'detect_model': 'weights/plate_detect.onnx',
        'rec_model': 'weights/plate_rec_color.onnx',
        'img_size': 640,
        'auto_recognition': True
    })
    rec = Recognition(opt)
    files = os.listdir('imgs')
    for file in files:
        raw = cv2.imread('imgs/' + file)
        if raw.shape[-1] == 4:
            raw = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        plates = rec.get_plates(raw)
        print(plates)
