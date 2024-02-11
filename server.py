import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

"""2024-02-07 01:41:50.110549: I tensorflow/core/platform/cpu_feature_guard.cc:193] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX2
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
OMP: Error #15: Initializing libiomp5, but found libiomp5md.dll already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. That is dangerous, since it can degrade performance or cause incorrect results. The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results. For more information, please see http://openmp.llvm.org/"""

from flask import Flask, redirect, render_template, request, jsonify, url_for
import numpy as np
import base64
from PIL import Image
from keras.models import load_model
from skimage.transform import resize
import cv2

app = Flask(__name__)

conv = load_model("./models/fruits.h5")
FRUITS = {0: "Apple", 1: "Banana", 2: "Grape", 3: "Pineapple"}
img_count = 0


@app.route("/", methods=["GET", "POST"])
def ready():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        data = request.form["payload"].split(",")[1]
        img = base64.decodebytes(data.encode())
            
        with open('temp.png', 'wb') as output:
            output.write(img)
        
        x = get_image()
        x = cropped(x)
        x = processed(x)
        
        classes = ["Apple", "Banana", "Grape", "Pineapple"]
        return jsonify({
            'preds': predictions(x),
            'classes': classes,
            'chart': True
        })
        
def convert(x):
    return int(255 - x)

def save_image(img, stage):
    cv2.imwrite(f'image_{stage}.png', img)
    
def normalize(data):
    return np.interp(data, [0, 255], [-1, 1])

def get_image():   
    
    img = Image.open('temp.png').convert('L')
    img = np.array(img)
    save_image(img, '0original')
    return img

def get_chart():
    
    img = Image.open('temp_chart.png')
    img = np.array(img)
    return img

def cropped(img):
    
    # Find the bounding box of the drawing
    rows = np.any(img < 255, axis=1)
    cols = np.any(img < 255, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    # Crop the image to the bounding box
    img = img[rmin:rmax, cmin:cmax]

    # Make the cropped image square
    length = max(rmax - rmin, cmax - cmin)
    img = np.pad(img, pad_width=((0, length - img.shape[0]), (0, length - img.shape[1])), mode='constant', constant_values=(255))

    save_image(img, '1cropped')
    return img

def processed(x):
    
    # resize input image to 28x28
    x = resize(x, (28, 28), preserve_range=True)
    save_image(x, '2resized')

    # darken the image by 90%
    for i in range(len(x)):
        for j in range(len(x)):
            if x[i][j] < 200:
                x[i][j] = max(0, x[i][j] - x[i][j] * 0.90)
    save_image(x, '3brightened')
    
    # invert the colors
    for i in range(28):
        x[i] = list(map(convert, x[i]))
    save_image(x, '4inverted')
    x = np.expand_dims(x, axis=0)
    x = np.reshape(x, (28, 28, 1))

    # normalize the values between -1 and 1
    x = normalize(x)
    save_image(x, '5normalized')
    
    return x

def predictions(img):
    
    val = conv.predict(np.array([img]))
    return [float(i) for i in val[0]]

def standardize(img):
    return resize(img, (600, 600), preserve_range=True)
        
@app.route("/save-image", methods=["POST"])
def save_image_route():
    global img_count
    img = standardize(cropped(get_image()))
    chart = get_chart()
    
    filename = 'static/saved_images/' + str(img_count) + '.png'
    chart_name = 'static/saved_charts/' + str(img_count) + '.png'
    cv2.imwrite(filename, img)
    cv2.imwrite(chart_name, chart)
    img_count += 1

    return redirect(url_for('ready'))

@app.route("/save-chart", methods=["POST"])
def save_chart():
    
    data = request.form["chart_data"].split(",")[1]
    img = base64.decodebytes(data.encode())
        
    with open('temp_chart.png', 'wb') as output:
        output.write(img)

    return render_template('image_saved.html')

@app.route("/display-images", methods=["GET"])
def display_images():
    image_names = os.listdir('static/saved_images')
    return render_template('display_images.html', image_names=image_names)


app.run(debug=True)
