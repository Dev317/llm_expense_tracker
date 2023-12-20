import os
import socket
from flask import Flask, request
from werkzeug.utils import secure_filename
from inference_util import extract, get_multimodal_model, get_image_documents, PROMPT_TEMPLATE
from data_model import Receipt
from datetime import datetime
import shutil


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f"{os.getcwd()}/upload"
MULTI_MODAL = get_multimodal_model()


@app.route("/api/health")
def health_check():
    return {
        "message": "Healthy service!",
        "hostname": socket.gethostname(),
        "ip_addres": socket.gethostbyname(socket.gethostname())
    }, 200


@app.route("/api/extract", methods=['POST'])
def extract_receipts():
    if "images" not in request.files:
        return {
            "message": "Missing images in request!"
        }, 400
    image_files = request.files.getlist("images")
    extraction_results = {}

    current_time = datetime.now().strftime("%d-%m%Y_%H%M%S")
    upload_dir = f"{app.config['UPLOAD_FOLDER']}/{current_time}"
    os.mkdir(upload_dir)

    try:
        for file in image_files:
            file_name = secure_filename(file.filename)
            path = os.path.join(upload_dir, file_name)
            file.save(path)

        img_documents = get_image_documents(upload_dir)
        for idx, doc in enumerate(img_documents):
            img_extracted_result = extract(Receipt,
                                        img_documents[idx: idx+1],
                                        PROMPT_TEMPLATE,
                                        MULTI_MODAL)
            extraction_results[doc.image_path] = {}
            for field in img_extracted_result:
                extraction_results[doc.image_path][field[0]] = field[1]

        return {
            "message": "Data extraction successful!",
            "data": extraction_results
        }, 200

    except Exception as ex:
        return {
            "message": f"Data extraction error occurred: {ex}"
        }, 404


if __name__ == '__main__':
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    os.mkdir(app.config['UPLOAD_FOLDER'])

    app.run(port="5000", debug=True)
