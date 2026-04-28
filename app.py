from flask import Flask, request, render_template_string
from PIL import Image
import imagehash, os, random

app = Flask(__name__)

# Database: hash → username
fingerprint_db = {}

# HTML template with dashboard
PAGE_TEMPLATE = """
<!doctype html>
<title>Digital Asset Protection Portal</title>
<h2>Digital Asset Protection System</h2>

<h3>Upload an Image</h3>
<form method=post enctype=multipart/form-data>
  <input type=text name=username placeholder="Enter User Name" required>
  <input type=file name=image required>
  <input type=submit value="Upload & Protect">
</form>

{% if result %}
  <h3>Result:</h3>
  <p>{{ result }}</p>
{% endif %}

<hr>
<h3>Registered Users & Fingerprints</h3>
<table border=1 cellpadding=5>
<tr><th>User</th><th>Fingerprint Hash</th></tr>
{% for h, u in fingerprint_db.items() %}
  <tr><td>{{ u }}</td><td>{{ h }}</td></tr>
{% endfor %}
</table>

<hr>
<h3>Leak Detection</h3>
<form method=post enctype=multipart/form-data action="/detect">
  <input type=file name=image required>
  <input type=submit value="Check Leak">
</form>

{% if leak_result %}
  <h4>Leak Detection Result:</h4>
  <p>{{ leak_result }}</p>
{% endif %}
"""

def add_invisible_fingerprint(img):
    """Simulate invisible fingerprint by altering random pixels slightly"""
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    for _ in range(50):  # change 50 random pixels
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        r, g, b = pixels[x, y]
        pixels[x, y] = (r, g, (b+1) % 255)  # tiny imperceptible change
    return img

@app.route("/", methods=["GET", "POST"])
def upload_image():
    result = None
    if request.method == "POST":
        username = request.form.get("username")
        file = request.files["image"]
        if file and username:
            img = Image.open(file.stream)
            hash_val = str(imagehash.phash(img))

            if hash_val in fingerprint_db:
                result = f"Image already registered → belongs to {fingerprint_db[hash_val]}"
            else:
                fingerprint_db[hash_val] = username
                result = f"New fingerprint stored → assigned to {username}"

            # Save fingerprinted image (optional visual demo)
            fp_img = add_invisible_fingerprint(img)
            os.makedirs("static", exist_ok=True)
            fp_img.save(f"static/{username}_fingerprinted.png")

    return render_template_string(PAGE_TEMPLATE, result=result,
                                  fingerprint_db=fingerprint_db, leak_result=None)

@app.route("/detect", methods=["POST"])
def detect_leak():
    leak_result = None
    file = request.files["image"]
    if file:
        img = Image.open(file.stream)
        hash_val = str(imagehash.phash(img))

        if hash_val in fingerprint_db:
            leak_result = f"Leak traced → Image belongs to {fingerprint_db[hash_val]}"
        else:
            leak_result = "No match found → Image not registered in system"

    return render_template_string(PAGE_TEMPLATE, result=None,
                                  fingerprint_db=fingerprint_db, leak_result=leak_result)

if __name__ == "__main__":
    app.run(debug=True)
