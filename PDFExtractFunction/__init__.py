import logging
import azure.functions as func
from azure.storage.blob import BlobClient
from io import BytesIO
from PDFExtracter import extract_all_transactions
import pyodbc
import os
import pandas as pd

def main(blob: func.InputStream):
    logging.info("🚀 Function loaded successfully.")

    logging.info(f"Triggered by blob: {blob.name}, Size: {blob.length} bytes")

    # Read PDF from blob
    pdf_bytes = blob.read()
    pdf_file = BytesIO(pdf_bytes)

    # Extract transactions
    transactions = extract_all_transactions(pdf_file, blob.name)

    if not transactions:
        logging.warning("No transactions extracted.")
        return

    df = pd.DataFrame(transactions)

    # DB connection (store values in App Settings)
    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    username = os.environ["SQL_USERNAME"]
    password = os.environ["SQL_PASSWORD"]
    driver = "{ODBC Driver 17 for SQL Server}"

    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Expenses (Date, Month, Year, Card, CardType, Transaction, Amount, CreditDebit, SubCategory, Category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row.Date, row.Month, row.Year, row.Card, row["Card Type"], row.Transaction, float(str(row.Amount).replace("₹", "").replace(",", "")), row["Credit/Debit"], row["Sub-Category"], row["Category"])

    conn.commit()
    cursor.close()
    conn.close()

    logging.info(f"Inserted {len(df)} transactions to SQL DB.")
