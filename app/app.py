import os, base64

from flask import Flask, jsonify, request, render_template, send_file
from hashlib import md5

from PIL import Image, ImageFont, ImageDraw

from cStringIO import StringIO

import colorsys

app = Flask(__name__)

def get_font(user_hash):
    fonts = [
        'ArchivoBlack-Regular',
        'BreeSerif-Regular',
        'Fresca-Regular',
        'Frijole-Regular',
        'Inconsolata-Bold',
        'Lato-Bold',
        'Merriweather-Bold',
        'OpenSans-Bold',
        'Oswald-Bold'
    ]
    name = fonts[int(user_hash[7:10], 16) % len(fonts)]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    font = os.path.join(dir_path, 'fonts', name + '.ttf')
    return ImageFont.truetype(font, size=24)

def calc_hash(string):
    m = md5()
    m.update(string)
    return m.hexdigest()

ALPHANUM = 'abcdefghijklmnopqrstuvwxyz0123456789'

def image_solution(h):
    result = ''
    for i in range(4):
        result += ALPHANUM[int(h[4*i:4*i+4], 16) % 36]
    return result

def real_image_solution(username, name):
    image_hash = calc_hash(username + name)
    return image_solution(image_hash)

def hsv_to_better_color(hsv):
    a, b, c = colorsys.hsv_to_rgb(*hsv)
    return (int(a*256), int(b*256), int(c*256))

def random_color_and_opposite(string):
    x = int(string, 16)
    y = float(x) / 16**len(string)
    hsv1 = (y, 1.0, 1.0)
    hsv2 = ((y + 0.5) % 1.0, 1.0, 1.0)
    return hsv_to_better_color(hsv1), hsv_to_better_color(hsv2)

def generate_image(username, name):
    user_hash = calc_hash(username)
    image_hash = calc_hash(username + name)
    solution = image_solution(image_hash)
    img = Image.new('RGB', (100, 50))
    draw = ImageDraw.Draw(img)
    font = get_font(user_hash)
    for i, letter in enumerate(solution):
        background_color, font_color = random_color_and_opposite(user_hash[5+2*i:9+2*i])
        draw.rectangle(((i*25, 0), (i*25 + 25, 50)), fill=background_color)
        rip = int(image_hash, 16)
        offset_x = rip % 10
        offset_y = (rip/64) % 20
        draw.text((i*25 + offset_x, offset_y), letter, font=font, fill=font_color)
    return img

def random_image(username):
    name = os.urandom(16).encode('hex')
    return generate_image(username, name), name

def serve_pil_image(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'JPEG', quality=50)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def pil_to_base64(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'JPEG', quality=50)
    return base64.b64encode(img_io.getvalue())

@app.route('/u/<username>/solution', methods=['POST'])
def test_solution(username):
    correct = 0
    incorrect = 0
    content = request.get_json(force=True)
    solved = set([])
    for solution in content['solutions']:
        if solution['name'] in solved:
            continue
        if solution['solution'] == real_image_solution(username, solution['name']):
            correct += 1
            # solved.add(solution['name'])
        else:
            incorrect += 1
    result = {
        'correct': correct,
        'incorrect': incorrect,
    }
    if correct >= 10000:
        result['message'] = "Congratulations! Marty and Doc are free. You are winrar."
        result['passcode'] = "TODO - fill in"
    return jsonify(result)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/u/<username>/', methods=['GET'])
def puzzle(username):
    return render_template('puzzle.html')

@app.route('/u/<username>/random_image', methods=['GET'])
def get_random_image(username):
    return serve_pil_image(random_image(username)[0])

@app.route('/u/<username>/image/<image_name>', methods=['GET'])
def get_image_name(username, image_name):
    return serve_pil_image(generate_image(username, image_name))

@app.route('/u/<username>/challenge', methods=['GET'])
def get_challenge(username):
    result = []
    for i in range(100):
        image, name = random_image(username)
        result.append({
            'jpg_base64': pil_to_base64(image),
            'name': name
        })
    return jsonify({'images': result})

if __name__ == "__main__":
    app.run(debug=True)
