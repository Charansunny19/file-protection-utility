import os
import uuid

from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

from crypto_utils import encrypt_file, decrypt_file


app = Flask(__name__)

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "File Protection Utility API is running"
    })


# ------------------------------------------------------------
# ENCRYPT
# ------------------------------------------------------------

@app.route("/encrypt", methods=["POST"])
def encrypt():

    try:

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No file selected."
            }), 400

        uploaded_file = request.files["file"]

        password = request.form.get("password", "")

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required."
            }), 400

        if uploaded_file.filename == "":
            return jsonify({
                "success": False,
                "message": "Invalid file."
            }), 400

        original_name = secure_filename(
            uploaded_file.filename
        )

        unique_id = uuid.uuid4().hex

        input_path = os.path.join(
            UPLOAD_FOLDER,
            unique_id + "_" + original_name
        )

        output_name = original_name + ".enc"

        output_path = os.path.join(
            OUTPUT_FOLDER,
            unique_id + "_" + output_name
        )

        uploaded_file.save(input_path)

        encrypt_file(
            input_path,
            output_path,
            password
        )

        # Remove temporary uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_name
        )

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ------------------------------------------------------------
# DECRYPT
# ------------------------------------------------------------

@app.route("/decrypt", methods=["POST"])
def decrypt():

    try:

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No encrypted file selected."
            }), 400

        uploaded_file = request.files["file"]

        password = request.form.get("password", "")

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required."
            }), 400

        if uploaded_file.filename == "":
            return jsonify({
                "success": False,
                "message": "Invalid file."
            }), 400

        original_name = secure_filename(
            uploaded_file.filename
        )

        unique_id = uuid.uuid4().hex

        input_path = os.path.join(
            UPLOAD_FOLDER,
            unique_id + "_" + original_name
        )

        if original_name.endswith(".enc"):
            output_name = original_name[:-4] + ".decrypted"
        else:
            output_name = original_name + ".decrypted"

        output_path = os.path.join(
            OUTPUT_FOLDER,
            unique_id + "_" + output_name
        )

        uploaded_file.save(input_path)

        decrypt_file(
            input_path,
            output_path,
            password
        )

        # Remove temporary encrypted file
        if os.path.exists(input_path):
            os.remove(input_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_name
        )

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ------------------------------------------------------------
# RUN SERVER
# ------------------------------------------------------------

if __name__ == "__main__":

    print()
    print("==========================================")
    print("     FILE PROTECTION UTILITY")
    print("==========================================")
    print("AES-256 Encryption")
    print("PBKDF2-HMAC-SHA256 Key Derivation")
    print("HMAC-SHA256 Integrity Verification")
    print()
    print("Server: http://127.0.0.1:5000")
    print("==========================================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )