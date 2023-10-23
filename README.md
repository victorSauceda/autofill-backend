# PDF Form Filler Web App

This is a web application that fills a PDF form with data from a CSV file. The field names in the PDF form and the CSV file are mapped using a JSON configuration file.

## Requirements

- Python 3
- Flask
- Gunicorn
- pandas
- pdfrw
- numpy
- argparse
- json
- uuid
- requests

You can install the required Python packages using pip:

### Run this command

`pip install Flask gunicorn pandas pdfrw numpy argparse json uuid requests`

## Usage

- `<csv_file>`: The CSV file with the data.
- `<pdf_file>`: The PDF form to fill.
- `<config_file>`: The JSON configuration file.

### Configuration file

The JSON configuration file should map the CSV field names to the PDF form field names. Here's an example:

```json
{
  "csv_field_name1": {
    "pdf_field": "pdf_field_name1",
    "required": true
  },
  "csv_field_name2": {
    "pdf_field": "pdf_field_name2",
    "required": false
  }
}
```

In this example, `csv_field_name1` and `csv_field_name2` are field names in the CSV file, and `pdf_field_name1` and `pdf_field_name2`` are field names in the PDF form. The required field indicates whether the field is required. If a required field is empty in the CSV file, the row will be skipped.

## Web App

To run the web application locally:

`python -m flask run`

Deployment for Production using Gunicorn

Ensure Gunicorn is installed:

`pip install gunicorn`

Start the application with Gunicorn:

`gunicorn app:app`

## Output

The command-line script generates a filled PDF form for each row in the CSV file. The file name of each PDF form is a unique identifier followed by .pdf.

The web application allows users to upload the necessary files and receive a zipped output containing the filled PDF forms.
