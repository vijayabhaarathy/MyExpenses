import logging
import os
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json

# Read from Application Settings (Function App → Configuration → App settings)
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

def main(blob: func.InputStream):
    logging.info(f"Triggered by blob: {blob.name}, Size: {blob.length} bytes")

    try:
        # Initialize Form Recognizer client
        client = DocumentAnalysisClient(
            endpoint=FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
        )

        # Analyze document with prebuilt model
        poller = client.begin_analyze_document(
            "prebuilt-document", blob.read()
        )
        result = poller.result()

        # Extracted results container
        extracted_data = {
            "fileName": blob.name,
            "pages": [],
            "tables": []
        }

        # Capture lines per page
        for page_idx, page in enumerate(result.pages):
            page_lines = [line.content for line in page.lines]
            extracted_data["pages"].append({
                "pageNumber": page_idx + 1,
                "lines": page_lines
            })

        # Capture tables
        for table in result.tables:
            table_rows = []
            for row_idx in range(table.row_count):
                row = [
                    cell.content for cell in table.cells if cell.row_index == row_idx
                ]
                table_rows.append(row)
            extracted_data["tables"].append(table_rows)

        # Log sample output
        logging.info("Extracted sample (first 5 lines):")
        for p in extracted_data["pages"][:1]:
            logging.info(p["lines"][:5])

        # TODO: Insert extracted_data into SQL Database here
        # For now, just dump JSON
        json_output = json.dumps(extracted_data, indent=2)
        logging.info(f"Extracted JSON: {json_output[:500]}...")  # Preview first 500 chars

    except Exception as e:
        logging.error(f"Error processing blob {blob.name}: {str(e)}")
