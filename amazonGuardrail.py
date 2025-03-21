import os
import boto3
from dotenv import load_dotenv
import json

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

client = session.client('bedrock')

guardrail_config = {
       "name": "TestGuardrail",
       "description": "Testing amazon guardrail",
       "filters": [
           {
               "type": "TOPIC",
               "topicPolicy": {
                   "topics": [
                       {
                           "name": "table related",
                           "action": "BLOCK"
                       }
                   ]
               }
           }
       ],
       "messages": {
           "blockedPrompt": "Sorry, I can't answer questions about creating/extracting table.",
           "blockedResponse": "Sorry, the model generated an answer that has an extracted information about the table."
       }
   }

response = client.create_guardrail(
    configuration=guardrail_config
)

guardrail_id = response['guardrailId']
print(f"Guardrail ID: {guardrail_id}")