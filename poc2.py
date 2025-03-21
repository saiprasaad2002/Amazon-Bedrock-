import boto3
import json
import base64
import pandas as pd
from dotenv import load_dotenv
import os
import PyPDF2

# Load environment variables
load_dotenv()

# Get AWS credentials and region from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Create a session with the credentials
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Initialize the Bedrock client using the session
bedrock = session.client('bedrock-runtime')

# Claude model ARN from environment variable
CLAUDE_MODEL_ARN = os.getenv('CLAUDE_MODEL_ARN')

def invoke_claude(prompt):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId=CLAUDE_MODEL_ARN,
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    document_name = os.getenv('DOCUMENT_NAME', 'poc_file.pdf')
    file_name = os.path.join(script_dir, document_name)
    
    if not os.path.exists(file_name):
        print(f"Error: The file '{document_name}' does not exist in the project folder.")
        return
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(file_name)
    
    # Prompt Claude to extract and structure table information
    prompt = f"""
    The following text is extracted from a PDF document. Please identify any tables in the text, 
    extract their content, and structure them as JSON. Each table should be represented as a list of dictionaries, 
    where each dictionary represents a row with column names as keys.

    Document text:
    {pdf_text}

    Please provide the structured table data as JSON.
    """
    
    claude_response = invoke_claude(prompt)
    
    print("Claude's extracted and structured table data:")
    print(claude_response)
    
    # Attempt to parse the JSON response
    try:
        structured_data = json.loads(claude_response)
        # If successful, you can now work with the structured data
        # For example, convert it to a pandas DataFrame
        if isinstance(structured_data, list) and len(structured_data) > 0:
            df = pd.DataFrame(structured_data[0])  # Assuming the first table
            print("\nFirst extracted table as DataFrame:")
            print(df)
        else:
            print("No table data found in the response.")
    except json.JSONDecodeError:
        print("Failed to parse Claude's response as JSON. Raw response:")
        print(claude_response)

if __name__ == "__main__":
    main()