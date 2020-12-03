import os
import gc
import io
import time
import base64
import logging

import numpy as np
from PIL import Image
import cv2

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

import detect


app = Flask(__name__)
CORS(app)

net = detect.load_model(model_name="u2net")

logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET"])
def ping():
    return "U^2-Net!"


@app.route("/remove", methods=["POST"])
def remove():
    start = time.time()

    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400

    #print(request.files['file'].read())

    # if request.files['file'].filename.rsplit('.', 1)[1].lower() not in ["jpg", "png", "jpeg"]:
    #     return jsonify({'error': 'invalid file format'}), 400

    data = request.files['file'].read()
    print(len(data))
    if len(data) == 0:
        return jsonify({'error': 'empty image'}), 400

    img = Image.open(io.BytesIO(data))

    output = detect.predict(net, np.array(img))
    output = output.resize((img.size), resample=Image.BILINEAR) # remove resample

    empty_img = Image.new("RGBA", (img.size), 0)
    new_img = Image.composite(img, empty_img, output.convert("L"))

    buffer = io.BytesIO()
    new_img.save(buffer, "PNG")
    new_img.save("image.png")
    buffer.seek(0)

    logging.info(f" Predicted in {time.time() - start:.2f} sec")
    
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

@app.route("/select", methods=["POST"])
def select():
    start = time.time()
    print('request'+str(request.get_data()))
    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400

    #print(request.files['file'].read())

    # if request.files['file'].filename.rsplit('.', 1)[1].lower() not in ["jpg", "png", "jpeg"]:
    #     return jsonify({'error': 'invalid file format'}), 400

    data = request.files['file'].read()
    print(len(data))
    if len(data) == 0:
        return jsonify({'error': 'empty image'}), 400

    img = Image.open(io.BytesIO(data))
    #background_img = Image.open(f'./image/{request.}')

    '''output = detect.predict(net, np.array(img))
    output = output.resize((img.size), resample=Image.BILINEAR) # remove resample

    empty_img = Image.new("RGBA", (img.size), 0)
    new_img = Image.composite(img, empty_img, output.convert("L"))'''

    buffer = io.BytesIO()
    new_img.save(buffer, "PNG")
    new_img.save("image.png")
    buffer.seek(0)

    logging.info(f" Predicted in {time.time() - start:.2f} sec")
    
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 5000)))
