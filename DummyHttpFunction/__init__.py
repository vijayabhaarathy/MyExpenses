import azure.functions as func
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🚀 Dummy HTTP function was called.")
    return func.HttpResponse("Hello from Dummy Function!", status_code=200)
