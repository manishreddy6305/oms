from mcp_router import MCPRouter
from bedrock import BedrockClient
import json
import re
from models.mistral_large import MistralLarge
from dotenv import load_dotenv

load_dotenv()

mcp_router = MCPRouter()
model = MistralLarge()
bedrock_client = BedrockClient()


def fetch_command(model_response):
    match = re.search(r"```json\\n(.*?)\\n```", json.dumps(model_response), re.DOTALL | re.IGNORECASE)
    if match:
        mcp_json_str = match.group(1).strip()
        cleaned = mcp_json_str.encode("utf-8").decode("unicode_escape")
        try:
            mcp_data = json.loads(cleaned)
            return mcp_data
        except json.JSONDecodeError:
            return {"action": "INVALID_RESPONSE"}
    else:
        return {"action": "NA"}
    
def get_message_as_per_command(command):
    if command['action'] == 'MCP':
        data = mcp_router.execute_tool(command["mcpDetails"])
        return {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": "execute_query_1",  # You need to propagate this from model's toolUse
                        "content": [
                            {"text": json.dumps(data)}
                        ]
                    }
                }
            ]
        }
    elif command['action'] == 'INVALID_RESPONSE':
        return {
            "role": "user",
            "content": [
                {"text": "Please strictly follow the output command json format"}
            ]
        }
    else:
        return None



if __name__ == "__main__":

    tools = json.loads(mcp_router.get_tools())
    messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": "what is the application id for mobile number 9915120241?"}
                    ]
                }
            ]
    
    while 1:
        api_response = bedrock_client.call_converse_api(model, messages, tools)
        model_response = api_response["output"]["message"]["content"][0]["text"]
        command = fetch_command(model_response)
        next_message = get_message_as_per_command(command)

        if next_message == None:
            break
        messages.append(next_message)


