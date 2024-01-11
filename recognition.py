import cv2
import time

from onnx import load_onnx_model, rec_by_session



class Recognition:
    def __init__(self, opt):
        session_detect, session_rec = load_onnx_model(opt.detect_model, opt.rec_model)
        img_size = (opt.img_size, opt.img_size)

        def detect(frame):
            start_time = time.time()
            result = rec_by_session(frame, img_size, session_detect, session_rec)
            print('recognition time: ', time.time() - start_time)
            return result

        self.detect = detect

    def get_plates(self, frame):
        if frame.shape[-1] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        result = self.detect(frame)
        if len(result) > 0:
            plates = []
            for i, r in enumerate(result):
                plate = {'no': r['plate_no'], 'color': r['plate_color']}
                plates.append(plate)
            return plates
        else:
            return None

    def start(self, fetch_image, callback):
        print('start plate recognition')
        last_rec_plates = {}
        while True:
            try:
                frame, jpg = fetch_image()
                if frame is None:
                    continue
                plates = self.get_plates(frame)
                can_send = True
                if plates is not None and len(plates) > 0:
                    # 如果last_rec_plates中不存在或者存在时间超过30秒，就发送
                    for p in plates:
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
                    callback(plates, jpg)
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
        img = cv2.imread('imgs/' + file)
        plates = rec.get_plates(img)
        print(plates)