import logging
import json
import azure.functions as func
from .PDFExtracter_v2 import extract_all_transactions

# Import the BlobServiceClient and other necessary libraries
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Please pass a JSON object in the request body.", status_code=400)

    file_path = req_body.get('filePath')

    if not file_path:
        return func.HttpResponse(
            "Please pass 'filePath' in the request body",
            status_code=400
        )

    try:
        # Connect to Blob Storage
        connect_str = "DefaultEndpointsProtocol=https;AccountName=<your_storage_account_name>;AccountKey=<your_storage_account_key>;EndpointSuffix=core.windows.net" # or use environment variable
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container="pdf-statements", blob=file_path.split("/")[-1])

        # Download the PDF file content
        pdf_data = blob_client.download_blob().readall()

        # Pass the file data to your extractor
        transactions = extract_all_transactions(pdf_data, file_path)

        if transactions:
            # Process the data (e.g., save to SQL) and return a success message
            return func.HttpResponse(
                json.dumps({"status": "success", "message": f"Successfully processed {len(transactions)} transactions from {file_path}"}),
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                "No transactions found in the PDF.",
                status_code=200,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return func.HttpResponse(
            f"An error occurred: {e}",
            status_code=500
        )
