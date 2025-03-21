import boto3
import json
import base64
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

bedrock = session.client('bedrock-runtime')
textract = session.client('textract')


# Claude model ARN from environment variable
CLAUDE_MODEL_ARN = os.getenv('CLAUDE_MODEL_ARN')

def invoke_claude(prompt):
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.5,
        "top_p": 1,
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId=CLAUDE_MODEL_ARN,
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['completion']

def analyze_document(file_name):
    with open(file_name, 'rb') as document:
        image_bytes = bytearray(document.read())
    
    response = textract.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=['TABLES', 'FORMS']
    )
    
    return response

def extract_tables(response):
    tables = []
    for item in response["Blocks"]:
        if item["BlockType"] == "TABLE":
            table = []
            for relationship in item.get("Relationships", []):
                if relationship["Type"] == "CHILD":
                    for cell_id in relationship["Ids"]:
                        cell = next((cell for cell in response["Blocks"] if cell["Id"] == cell_id), None)
                        if cell and "Text" in cell:
                            table.append(cell["Text"])
            tables.append(table)
    return tables

def main():
    # Example usage
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the document in the project folder
    document_name = os.getenv('DOCUMENT_NAME', 'poc_file.pdf')
    file_name = os.path.join(script_dir, document_name)
    
    # Check if the file exists
    if not os.path.exists(file_name):
        print(f"Error: The file '{document_name}' does not exist in the project folder.")
        return
    
    # Analyze document with Textract
    textract_response = analyze_document(file_name)
    extracted_tables = extract_tables(textract_response)
    
    # Convert extracted tables to pandas DataFrames
    dfs = []
    for table in extracted_tables:
        # Assuming the first row is headers
        headers = table[:len(table)//3]  # Adjust this based on your table structure
        data = table[len(table)//3:]
        df = pd.DataFrame([data[i:i+len(headers)] for i in range(0, len(data), len(headers))], columns=headers)
        dfs.append(df)
    
    # Example: Print the first table
    if dfs:
        print("First extracted table:")
        print(dfs[0])
    
    # Example: Use Claude to interpret the table
    if dfs:
        table_description = dfs[0].to_string()
        prompt = f"Here's a table extracted from a document:\n\n{table_description}\n\nCan you describe what this table represents and summarize its key information?"
        claude_response = invoke_claude(prompt)
        print("\nClaude's interpretation of the table:")
        print(claude_response)

if __name__ == "__main__":
    main()