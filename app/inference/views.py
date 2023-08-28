from flask import jsonify, Blueprint, request, Response, current_app
from mongoengine import *
import cv2, atexit
from time import sleep
from app.decorators import api_login_required, admin_required

inference_bp = Blueprint('inference', __name__, url_prefix='/inference/')

def gather_img(model_daemon):
    while True:
        FPS = 4
        T = 1/FPS
        sleep(T)
        img = model_daemon.get_current_frame()
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

@inference_bp.route('/footage_stream/')
@api_login_required
def footage_stream():
    return Response(gather_img(current_app.model_daemon), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@inference_bp.route('/get_seg/')
@api_login_required
@admin_required
def get_seg():
    user_seg = current_app.model_daemon.user_seg
    vid = current_app.model_daemon.vid
    shape = [vid.new_w, vid.new_h] if vid is not None else [1280, 720]
    if request.args.get('format') == 'xsys':
        try:
            xs = [item[0] for item in user_seg]
            ys = [item[1] for item in user_seg]
        except:
            xs = []
            ys = []
        return jsonify({'xsys': [xs, ys], 'shape': shape})
    return jsonify({'xyxy': user_seg, 'shape': shape})

@inference_bp.route('/set_seg/', methods=['POST'])
@api_login_required
@admin_required
def set_seg():
    payload = request.json
    if payload.get('xsys') is not None:
        data = payload['xsys']
        if (
            isinstance(data, list)
            and all(isinstance(item, list) and len(item) == 2 for item in data)
        ):
            current_app.model_daemon.set_seg(data)
            return jsonify({"message": "Sucesso."}), 200
        else:
            return jsonify({"error": "Formato incorreto. Dados devem conter quatro pares de coordenada."}), 400
    else:
        return jsonify({"error": "Arquivos não encontrados no payload."}), 400