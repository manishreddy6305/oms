from dotenv import load_dotenv
import os
import boto3
import json


project_root = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_root, '.env')

load_dotenv(dotenv_path=env_path)

class BedrockClient:
    def __init__(self):
        self.bedrockRuntime = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION"))

    def call_converse_api(self, model_id, system_prompt, tools, messages):

        response = self.bedrockRuntime.converse(
            modelId=model_id,
            system=[
                {
                    "text": system_prompt
                }
            ],
            messages=messages,
            toolConfig=tools,
        )

        # print(f"\n\nModelReturned: f{json.dumps(response)}")

        return response
    
    # def prepare_tools_config(self, tools) :
    #     # tools = json.loads(mcpRouter.get_tools())
    #     tool_config = {
    #         "tools": [{"toolSpec": t} for t in tools["tools"]]
    #     }

    #     return tool_config