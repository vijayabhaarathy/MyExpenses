import logging
import os
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Use environment variables for security
endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("FORM_RECOGNIZER_KEY")

def main(blob: func.InputStream):
    logging.info(f"Processing file: {blob.name}, Size: {blob.length} bytes")

    # Init Form Recognizer client
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )

    # Send file to Form Recognizer
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-document", blob.read()
    )
    result = poller.result()

    # Extract text and tables
    extracted_data = []
    for page in result.pages:
        for line in page.lines:
            extracted_data.append(line.content)

    for table in result.tables:
        for cell in table.cells:
            logging.info(f"Table cell ({cell.row_index},{cell.column_index}): {cell.content}")
            extracted_data.append(cell.content)

    logging.info(f"Extracted Data: {extracted_data[:20]}")  # Preview first 20

    # TODO: Insert extracted_data into SQL DB (Phase 1 continuation)
