from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
import io
import os

# 🔥 Pillow memory optimization
Image.MAX_IMAGE_PIXELS = None
Image.warnings.simplefilter("ignore")

app = Flask(__name__)
CORS(app)

# ✅ LOWEST RAM model (Render Free SAFE)
session = new_session("modnet_photographic")

def resize_image(img, max_size=512):   # 👈 VERY IMPORTANT
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

    # ⚠️ convert only once
    original = Image.open(file.stream).convert("RGBA")

    resized = resize_image(original)
    result = remove(resized, session=session)

    # restore original size (optional but safe)
    result = result.resize(original.size)

    buf = io.BytesIO()
    result.save(buf, format='PNG', optimize=False)  # optimize=False saves RAM
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        threaded=False   # 👈 SINGLE THREAD (LOW RAM)
    )
