from flask import Flask, render_template, Response, request, jsonify
from thermal_camera import ThermalCamera
import cv2

app = Flask(__name__)
camera = ThermalCamera()

@app.route('/')
def index():
    colormaps = ['inferno', 'magma', 'plasma', 'viridis', 'cividis', 'jet', 'nipy_spectral']
    camera.generate_legend()
    return render_template('index.html', colormaps=colormaps, current_colormap=camera.colormap)

@app.route('/change_colormap', methods=['POST'])
def change_colormap():
    data = request.get_json()
    colormap = data['colormap']
    camera.set_colormap(colormap)
    return jsonify(success=True)

def gen():
    while True:
        frame = camera.get_frame()
        processed_frame = camera.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/filter', methods=['GET'])
def toggle_filter():
    camera.toggle_filter()
    return ("Filtering Toggled")

@app.route('/temperature', methods=['POST'])
def get_temperature():
    x = float(request.form['x'])
    y = float(request.form['y'])
    frame = camera.get_frame()

    image_width, image_height = 320, 240
    sensor_width, sensor_height = 32, 24

    sensor_x = int((x / image_width) * sensor_width)
    sensor_y = int((y / image_height) * sensor_height)

    if sensor_x >= sensor_width:
        sensor_x = sensor_width - 1
    if sensor_y >= sensor_height:
        sensor_y = sensor_height - 1

    temperature = frame[sensor_y, sensor_x]
    return jsonify(temperature=temperature)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

