from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

# ✅ LOW-RAM model (Render Free friendly)
session = new_session("isnet-general-use")

def resize_image(img, max_size=640):   # 👈 smaller = less RAM
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        return img.resize(
            (int(w * ratio), int(h * ratio)),
            resample=Image.BILINEAR
        )
    return img

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    file = request.files['image']
    original = Image.open(file.stream).convert("RGBA")

    resized = resize_image(original)
    removed = remove(resized, session=session)
    removed = removed.resize(original.size)

    buf = io.BytesIO()
    removed.save(buf, format='PNG', optimize=True)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
