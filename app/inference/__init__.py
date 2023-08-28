from flask import url_for
import atexit
import threading
import numpy as np
from time import sleep
import random, cv2
import csv, os

def save_coordinates(coordinates, id, archive):
    # Lê o conteúdo do arquivo CSV existente, se houver
    current_data = {}
    try:
        with open(archive, 'r') as csv_archive:
            reader = csv.reader(csv_archive)
            for line in reader:
                current_data[line[0]] = line[1]
    except FileNotFoundError:
        pass

def generate_random_img(res):
    return np.random.randint(0, 255, size=(*res, 3), dtype=np.uint8)

def generate_random_text_image(width, height, text, font_scale):
    bg_color = np.random.randint(0, 256, 3)

    image = np.full((height, width, 3), bg_color, dtype=np.uint8)

    text_x = random.randint(50, width - 50)
    text_y = random.randint(50, height - 50)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_color = (255, 255, 255)
    thickness = 2

    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

    text_x -= text_width // 2
    text_y += text_height // 2

    cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)

    return image

class ModelDaemon(threading.Thread):
    def __init__(self, weights_path, demo_url, save_folder, seg_file_path=None, f=30):
        super().__init__(daemon=True)
        self.weights_path = weights_path
        self.demo_url = demo_url
        self.vid = None
        self.current_frame = None
        self.source = demo_url
        self.f = f
        self.running = False
        self.finished = False
        self.model = None
        self.save_folder = save_folder
        self.seg_file_path = seg_file_path
        self.user_seg = None

    def get_current_frame(self):
        if self.current_frame is not None:
            return self.current_frame
        return generate_random_img((1280, 720))
    
    def placeholder_loop(self):
        self.running = True
        while self.running:
            self.current_frame = generate_random_text_image(1280, 720, 'This is a test!', 1)
            sleep(1 / self.f)
        self.finished = True
    
    def set_seg(self, seg): 
        if len(seg) > 3:
            self.user_seg =  [[round(xy) for xy in l] for l in seg]
            if self.seg_file_path and os.path.exists(self.seg_file_path):
                save_coordinates(self.user_seg, self.demo_url, self.seg_file_path)
            return True
        return False

    def stop_running(self):
        self.running = False
        while not self.finished:
            sleep(0.01)

    def video_loop(self):
        #implemente a lógica do modelo aqui.

        self.placeholder_loop()

    def run(self):
        if not self.weights_path or not self.demo_url:
            print('YOLO model not detected. Using placeholder loop...')
            self.placeholder_loop()
        else:
            self.video_loop()

def kill_thread(model_daemon):
    print('\n\STOPPING MODEL')
    try:
        model_daemon.stop_running()
    except KeyboardInterrupt:
        print('\n\nFINISHED')
    

def create_module(app):
    from .views import inference_bp
    app.model_daemon = ModelDaemon(app.config.get('YOLO_WEIGHTS'), app.config.get('DEMO_URL'), seg_file_path=app.config.get('COORDENADAS'), save_folder=app.config.get('UPLOAD_FOLDER'))
    app.model_daemon.start()
    atexit.register(kill_thread, model_daemon=app.model_daemon)
    app.register_blueprint(inference_bp)