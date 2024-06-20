from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, jsonify
import os
import psutil
import socket
import webbrowser
import threading

app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip_addresses():
    ip_addresses = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                ip_addresses.append(snic.address)
    return ip_addresses

@app.route('/')
def home():
    ip_addresses = get_local_ip_addresses()
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Upload and Download Files</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css" 
                integrity="sha512-jnSuA4Ss2PkkikSOLtYs8BlYIeeIK1h99ty4YfvRPAlzr377vr3CXDb7sb7eEEBYjDtcYj+AjBH3FLv5uSJuXg==" 
                crossorigin="anonymous" referrerpolicy="no-referrer" />
            <style>
                html, body {
                    background-color: #eaecea
                }
                .file-list {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .file-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                .file-name {
                    flex-grow: 1;
                }
         
            </style>
        </head>
        <body>
            <div class="bg-white">
                <div class="container">
                    <header class="d-flex flex-wrap justify-content-center py-3 mb-4 border-bottom">
                    <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto link-body-emphasis text-decoration-none">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-cloud-arrow-up-fill me-3" viewBox="0 0 16 16">
                            <path d="M8 2a5.53 5.53 0 0 0-3.594 1.342c-.766.66-1.321 1.52-1.464 2.383C1.266 6.095 0 7.555 0 9.318 0 11.366 1.708 13 3.781 13h8.906C14.502 13 16 11.57 16 9.773c0-1.636-1.242-2.969-2.834-3.194C12.923 3.999 10.69 2 8 2m2.354 5.146a.5.5 0 0 1-.708.708L8.5 6.707V10.5a.5.5 0 0 1-1 0V6.707L6.354 7.854a.5.5 0 1 1-.708-.708l2-2a.5.5 0 0 1 .708 0z"/>
                        </svg>
                        <span class="fs-4">LAN Drive</span>
                    </a>
                    </header>
                </div>
            </div>
            <div class="container">
                <div class="row p-3 bg-white rounded-2">
                {% for ip in ip_addresses %}
                  <div class="col">
                    <div id="qrcode-{{ loop.index }}"></div>
                    <a href="http://{{ ip }}:5000" target="_blank" class="text-muted">http://{{ ip }}:5000</a>
                  </div>
                {% endfor %}
                </div>

                <div class="py-5 px-3 bg-white rounded-2 my-3 px-4 row">
                    <form method=post enctype=multipart/form-data action="/upload">
                      <input type=file name=file class="form-control form-control-lg">
                      <input type=submit value=Upload class="btn btn-lg btn-secondary ms-2 my-3 w-100">
                    </form>
                </div>
                <div class="h2 border-bottom py-3">All Files</div>
                <div class="file-list bg-white p-3 rounded-2 row">
                {% for filename in files %}
                  <div class="file-item p-2">
                    <a class="file-name" href="{{ url_for('download', filename=filename) }}" target="_blank">{{ filename }}</a>
                    <a href="{{ url_for('download', filename=filename) }}" download>
                      <button class="btn btn-secondary">Download</button>
                    </a>
                  </div>
                {% endfor %}
                </div>
            </div>
            <script>

            const ipAddresses = {{ ip_addresses|tojson }};
            ipAddresses.forEach((ip, index) => {
                
                var qrcode = new QRCode(document.getElementById(`qrcode-${index + 1}`), {
                    text: `http://${ip}:5000`,
                    width: 128,
                    height: 128,
                    colorDark: "#000000",
                    colorLight: "#ffffff",
                    correctLevel: QRCode.CorrectLevel.H
                });
            });
                
            </script>
        </body>
        </html>
    ''', files=os.listdir(app.config['UPLOAD_FOLDER']), ip_addresses=ip_addresses)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('home'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000)
