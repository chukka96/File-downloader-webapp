from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import threading
import zipfile
import shutil
from urllib.parse import urlparse

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
ZIP_FOLDER = "zips"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

progress = {
    "current": 0,
    "total": 0,
    "status": "idle"
}

history = []


def clear_folders():
    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    shutil.rmtree(ZIP_FOLDER, ignore_errors=True)

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(ZIP_FOLDER, exist_ok=True)


def download_files(urls):
    global progress, history

    clear_folders()
    history.clear()

    progress["total"] = len(urls)
    progress["current"] = 0
    progress["status"] = "running"

    for index, url in enumerate(urls, start=1):

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            filename = os.path.basename(
                urlparse(url).path
            )

            if not filename:
                filename = f"file_{index}"

            filename = f"{index}_{filename}"

            filepath = os.path.join(
                DOWNLOAD_FOLDER,
                filename
            )

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            history.append({
                "file": filename,
                "status": "Success"
            })

        except Exception as e:

            history.append({
                "file": url,
                "status": f"Failed - {str(e)}"
            })

        progress["current"] = index

    create_zip()

    progress["status"] = "completed"


def create_zip():

    zip_path = os.path.join(
        ZIP_FOLDER,
        "downloads.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in os.listdir(DOWNLOAD_FOLDER):

            full_path = os.path.join(
                DOWNLOAD_FOLDER,
                file
            )

            zipf.write(
                full_path,
                arcname=file
            )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_download():

    urls = request.json.get("urls", [])

    thread = threading.Thread(
        target=download_files,
        args=(urls,)
    )

    thread.start()

    return jsonify({"message": "Started"})


@app.route("/progress")
def get_progress():
    return jsonify(progress)


@app.route("/history")
def get_history():
    return jsonify(history)


@app.route("/download-zip")
def download_zip():

    zip_path = os.path.join(
        ZIP_FOLDER,
        "downloads.zip"
    )

    return send_file(
        zip_path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)