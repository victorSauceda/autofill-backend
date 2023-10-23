from flask import Flask, render_template, request, send_from_directory
import os
import zipfile
import requests
from flask_frozen import Freezer
app = Flask(__name__)
freezer = Freezer(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'pdf', 'json'}

# replace with your API endpoint
API_ENDPOINT_URL = "https://autofill-backend.onrender.com/"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'csv_file' not in request.files or 'pdf_file' not in request.files or 'config_file' not in request.files:
            return 'No file part'

        csv_file = request.files['csv_file']
        pdf_file = request.files['pdf_file']
        config_file = request.files['config_file']

        if csv_file.filename == '' or pdf_file.filename == '' or config_file.filename == '':
            return 'No selected file'

        if csv_file and allowed_file(csv_file.filename) and pdf_file and allowed_file(pdf_file.filename) and config_file and allowed_file(config_file.filename):
            csv_filename = os.path.join(
                app.config['UPLOAD_FOLDER'], csv_file.filename)
            pdf_filename = os.path.join(
                app.config['UPLOAD_FOLDER'], pdf_file.filename)
            config_filename = os.path.join(
                app.config['UPLOAD_FOLDER'], config_file.filename)

            csv_file.save(csv_filename)
            pdf_file.save(pdf_filename)
            config_file.save(config_filename)

            # Calling the external API to process the files
            response = requests.post(
                API_ENDPOINT_URL,
                files={
                    'csv_file': open(csv_filename, 'rb'),
                    'pdf_file': open(pdf_filename, 'rb'),
                    'config_file': open(config_filename, 'rb')
                }
            )

            if response.status_code == 200:
                zip_filename = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'result.zip')
                with open(zip_filename, 'wb') as f:
                    f.write(response.content)
            else:
                return 'Error processing the files with the API'

            # Return the zipped file for download
            return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=os.path.basename(zip_filename), as_attachment=True)

    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <title>Upload Files</title>
      </head>
      <body class="bg-light">
        <div class="container my-5">
          <div class="card">
            <div class="card-header">
                <div class="text-center my-4">
                    <h1 class="display-4">Clear My Record</h1>
                    <p class="lead">PDF Auto-filler 🦭</p>
                </div>
            </div>
            <div class="card-body">
              <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                  <label for="csv_file">CSV File</label>
                  <input type="file" class="form-control-file" name="csv_file">
                </div>
                <div class="form-group">
                  <label for="pdf_file">PDF File</label>
                  <input type="file" class="form-control-file" name="pdf_file">
                </div>
                <div class="form-group">
                  <label for="config_file">Config File</label>
                  <input type="file" class="form-control-file" name="config_file">
                </div>
                <button type="submit" class="btn btn-primary">Upload</button>
              </form>
            </div>
          </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.3/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
      </body>
    </html>
    '''


if __name__ == "__main__":
    app.run()
