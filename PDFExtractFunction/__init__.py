import logging
import os
import json
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Environment variables (set in Function App > Configuration)
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

def main(blob: func.InputStream):
    logging.info(f"Triggered by blob: {blob.name}, Size: {blob.length} bytes")

    try:
        # Init Form Recognizer client
        client = DocumentAnalysisClient(
            endpoint=FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
        )

        # Analyze PDF with prebuilt-document model
        poller = client.begin_analyze_document(
            model_id="prebuilt-document",
            document=blob.read()
        )
        result = poller.result()

        extracted_data = {"fileName": blob.name, "pages": [], "tables": []}

        # Extract text lines
        for page_idx, page in enumerate(result.pages):
            lines = [line.content for line in page.lines]
            extracted_data["pages"].append({
                "pageNumber": page_idx + 1,
                "lines": lines
            })

        # Extract tables
        for table in result.tables:
            rows = []
            for row_idx in range(table.row_count):
                row = [cell.content for cell in table.cells if cell.row_index == row_idx]
                rows.append(row)
            extracted_data["tables"].append(rows)

        # Log preview
        logging.info(f"Extracted JSON preview: {json.dumps(extracted_data, indent=2)[:500]}")

        # TODO: Insert into SQL DB in Phase 2
        # For now, just log the extracted content

    except Exception as e:
        logging.error(f"Error processing {blob.name}: {str(e)}")
