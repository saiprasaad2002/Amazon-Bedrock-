import boto3
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Setup Boto3 session
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# Create Bedrock runtime client
bedrock_client = session.client('bedrock-runtime')

def sanitize_filename(filename):
    # Allow only alphanumeric characters, whitespaces, hyphens, parentheses, square brackets
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-\(\)\[\]]+', '', filename)
    # Ensure not more than one consecutive whitenesspace character
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()

def invoke_converse_document(bedrock_client, model_id, prompt, document_path):
    with open(document_path, "rb") as document_file:
        document_bytes = document_file.read()
        
    original_filename = os.path.basename(document_path)
    sanitized_name = sanitize_filename(original_filename)
    
    document_block = {
        "role": "user",
        "content": [
            {"text": prompt},
            {
                "document": {
                    "format": document_path.split('.')[-1],
                    "name": sanitized_name,
                    "source": {"bytes": document_bytes}
                }
            }
        ]
    }
    
    # Sending the message
    response = bedrock_client.converse(
        modelId=model_id,
        messages=[document_block]
    )
    
    return response

# Use the Amazon Nova Lite ARN instead of the Claude Model ARN
model_id = os.getenv('CLAUDE3.7_MODEL_ARN')
prompt = "Give me the explanation for the graphical representation of Inflation away from home vs at home"
document_path = "D:\\Textract_POC\\poc2.pdf"
response = invoke_converse_document(bedrock_client, model_id, prompt, document_path)
print(response['output']['message']['content'][0]['text'])