# main.py - YOLO Camera Stream App
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window

import cv2
import socket
import struct
import threading
import numpy as np
from cryptography.fernet import Fernet
import os

# 生成或加载密钥
def get_key():
    key_file = '/sdcard/yolo_key.txt' if os.path.exists('/sdcard') else 'yolo_key.txt'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read().strip()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

KEY = get_key()
cipher = Fernet(KEY)

class CameraStream(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # 标题
        self.add_widget(Label(
            text='YOLO Camera Stream',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            color=(1, 1, 1, 1)
        ))
        
        # 服务器IP输入
        self.ip_input = TextInput(
            hint_text='Enter server IP (e.g. 192.168.43.1)',
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.ip_input)
        
        # 状态显示
        self.status = Label(
            text='Ready - Key: ' + KEY.decode()[:20] + '...',
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1),
            font_size='12sp'
        )
        self.add_widget(self.status)
        
        # 按钮区域
        btn_box = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=10)
        
        self.start_btn = Button(
            text='START STREAM',
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.start_btn.bind(on_press=self.start_stream)
        btn_box.add_widget(self.start_btn)
        
        self.stop_btn = Button(
            text='STOP',
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.stop_btn.bind(on_press=self.stop_stream)
        btn_box.add_widget(self.stop_btn)
        
        self.add_widget(btn_box)
        
        # 摄像头预览
        self.preview = Image()
        self.add_widget(self.preview)
        
        self.streaming = False
        self.sock = None
        self.capture = None
        self.stream_thread = None
    
    def start_stream(self, instance):
        ip = self.ip_input.text.strip()
        if not ip:
            self.status.text = 'Error: Please enter server IP'
            return
        
        self.streaming = True
        self.status.text = f'Connecting to {ip}:8888...'
        self.start_btn.background_color = (0.3, 0.5, 0.3, 1)
        
        self.stream_thread = threading.Thread(target=self.stream_loop, args=(ip,))
        self.stream_thread.daemon = True
        self.stream_thread.start()
    
    def stop_stream(self, instance):
        self.streaming = False
        self.status.text = 'Stopped'
        self.start_btn.background_color = (0.2, 0.7, 0.3, 1)
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        
        if self.capture:
            self.capture.release()
            self.capture = None
    
    def stream_loop(self, server_ip):
        try:
            # 连接服务器
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((server_ip, 8888))
            self.sock.settimeout(None)
            
            # 打开摄像头
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.capture.isOpened():
                self.status.text = 'Error: Cannot open camera'
                return
            
            self.status.text = 'Streaming... Press STOP to quit'
            
            frame_count = 0
            while self.streaming:
                ret, frame = self.capture.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # 每3帧更新一次预览（降低UI负载）
                if frame_count % 3 == 0:
                    Clock.schedule_once(lambda dt, f=frame: self.update_preview(f), 0)
                
                # 编码JPEG
                ret, jpeg = cv2.imencode('.jpg', frame, [
                    cv2.IMWRITE_JPEG_QUALITY, 65,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1
                ])
                if not ret:
                    continue
                
                # 加密
                encrypted = cipher.encrypt(jpeg.tobytes())
                size = len(encrypted)
                
                # 发送：大小(4字节) + 数据
                header = struct.pack('!I', size)
                self.sock.sendall(header)
                self.sock.sendall(encrypted)
            
        except Exception as e:
            self.status.text = f'Error: {str(e)}'
            self.streaming = False
    
    def update_preview(self, frame):
        # 缩小预览尺寸降低GPU负载
        small = cv2.resize(frame, (320, 240))
        buf = cv2.flip(small, 0).tobytes()
        
        texture = Texture.create(
            size=(small.shape[1], small.shape[0]),
            colorfmt='bgr'
        )
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.preview.texture = texture

class YoloCameraApp(App):
    def build(self):
        return CameraStream()

if __name__ == '__main__':
    YoloCameraApp().run()