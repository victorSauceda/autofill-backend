import pdfrw
import pandas as pd
import json
import uuid
import os
import zipfile


def autofill_pdf(csv_path, pdf_path, config_path):
    """
    Fills a PDF form for each row in a CSV file based on configuration from a JSON file.

    Args:
        csv_path (str): Path to the CSV file.
        pdf_path (str): Path to the PDF form to fill.
        config_path (str): Path to the JSON configuration file.

    Returns:
        str: Path to the zipped file containing filled PDF forms.
    """
    # Ensure the output directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Read the CSV file
    data = pd.read_csv(csv_path)

    # Read the configuration file
    with open(config_path, 'r') as f:
        config = json.load(f)

    output_files = []

    for index, row in data.iterrows():

        # Read the PDF form for each row to ensure a fresh template
        template_pdf = pdfrw.PdfReader(pdf_path)

        # Create a dictionary with data from the current row
        row_data = {}
        skip_row = False
        for k, v in row.to_dict().items():
            if k in config and config[k]['pdf_field']:
                if config[k]['required'] and (pd.isnull(v) or v == '' or v == ' '):
                    print(
                        f"Skipping row {index} due to missing required field {k}.")
                    skip_row = True
                    break
                row_data[config[k]['pdf_field']] = int(v) if pd.notnull(
                    v) and str(v).replace('.', '', 1).isdigit() else v

        # Skip the row if any required field is missing
        if skip_row:
            continue

        # Fill the form fields
        for page in template_pdf.pages:
            annotations = page.Annots
            if annotations:
                for annotation in annotations:
                    field_name = str(annotation['/T'])
                    if field_name in row_data:
                        annotation.update(pdfrw.PdfDict(
                            V=str(row_data[field_name]), AP=""))

        # Set the NeedAppearances flag to ensure the viewer generates field appearances
        if '/AcroForm' not in template_pdf.Root.keys():
            template_pdf.Root.AcroForm = pdfrw.PdfDict()
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(
            NeedAppearances=pdfrw.PdfObject('true')))

        # Generate a unique identifier for the file name
        unique_id = uuid.uuid4()

        # Save the filled form
        output_filename = os.path.join("uploads", f"{unique_id}.pdf")
        pdfrw.PdfWriter().write(output_filename, template_pdf)

        output_files.append(output_filename)

    # After processing all rows and creating the filled PDFs, zip them
    zip_name = os.path.join("uploads", "autofilled_pdfs.zip")
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))

    # Clean up by removing the individual filled PDF files
    for file in output_files:
        os.remove(file)

    return zip_name
