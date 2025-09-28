
from dotenv import load_dotenv
from client import KnowledgeMCPClient
import os
import json



client = KnowledgeMCPClient(
)


print(f"3. \n\n\n\n\n\n {json.dumps(client.get_knowledge(name="apply_application_flow"))} \n\n\n\n\n")