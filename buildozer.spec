[app]
title = YOLO Camera
package.name = yolocamera
package.domain = com.yolo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt
version = 1.0
requirements = python3,kivy==2.2.1,opencv-python==4.8.1.78,cryptography==41.0.7,pillow,numpy
orientation = portrait
fullscreen = 0
android.presplash_color = #1a1a1a
android.icon = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# API级别
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# 目标架构（arm64-v8a为现代手机，armeabi-v7a兼容旧机）
android.arch = arm64-v8a

# 权限
android.permissions = 
    CAMERA,
    INTERNET,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    FOREGROUND_SERVICE,
    WAKE_LOCK,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE

# 特性声明
android.features = 
    android.hardware.camera,
    android.hardware.camera.autofocus

# 防止优化导致的问题
android.add_aars = 
android.gradle_dependencies = 

# 启动模式
android.launch_mode = standard

# 屏幕支持
android.supports_any_density = True

[p4a]
# Python for Android版本
p4a.branch = master

# 本地 recipes（如果需要自定义OpenCV编译）
p4a.local_recipes = 

# 额外参数
p4a.extra_args = 
    --enable-android-native-libraries
    --add-requirement=kivy