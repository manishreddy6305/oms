from mcp_router import MCPRouter
from bedrock import BedrockClient
import json
from models.mistral_large import MistralLarge
from models.nova_premier import NovaPremier
from dotenv import load_dotenv
from db.execution_store_factory import get_conversation_store
from objects.execution import Execution
import os
import traceback
from utils import file_utils
import uuid

load_dotenv()

mcp_router = MCPRouter()
#model = MistralLarge()
model = NovaPremier()
bedrock_client = BedrockClient()
store=get_conversation_store()


def handle_tool_use(execution: Execution, tool_use_block):
    """ syntax
        {
            "toolUseId": "tooluse_j6t7fEhGSFaQE_x8itQfug",
            "name": "execute_query",
            "input": {
                "database_id": 2,
                "query": "SELECT application_id FROM user_application WHERE mobile_number = '9915120241'"
            }
        }
    """
    tool_use_id = tool_use_block["toolUseId"]
    tool_name = tool_use_block["name"]
    params = tool_use_block.get("input", {})

    result = mcp_router.execute_tool(
            execution, 
            {
                "tool_name": tool_name,
                "params": params
            }
    )

    execution.mcp_calls.append(tool_name)

    return {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": tool_use_id,
                    "content": [
                        {"text": json.dumps(result)}
                    ]
                }
            }
        ]
    }

tools = json.loads(mcp_router.get_tools())

def recordMetrics(model_response, execution: Execution):
    execution.input_token.append(model_response["usage"]["inputTokens"])
    execution.output_tokens.append(model_response["usage"]["outputTokens"])
    execution.model_calls += 1
    execution.model_latencies.append(model_response["metrics"]["latencyMs"])


def get_system_prompt(execution: Execution):
    prompt_version = execution.prompt_version

    DATABASE_SCHEMA = file_utils.read_file(f"./knowledge/{prompt_version}/schemas.md")
    SEED_INFO = file_utils.read_file(f"./knowledge/{prompt_version}/seed_info.md")
    SYSTEM_PROMPT = file_utils.read_file(f"./knowledge/{prompt_version}/system_prompt.md")
    LOGS_DEBUGGING = file_utils.read_file(f"./knowledge/{prompt_version}/debugging_with_logs_detailed.md")
    CONLUENCE_PROMPT = file_utils.read_file(f"./knowledge/{prompt_version}/confluence_playbook.md")

    prompt = f"""
        {SYSTEM_PROMPT}
        
        Confluence Context: 
        {CONLUENCE_PROMPT}

        System Context:
        {SEED_INFO}

        Schema:
        {DATABASE_SCHEMA}

        Debugging Logs:
        {LOGS_DEBUGGING}

    """

    return prompt



def process(prompt_version, key, seed) -> Execution:
    if not seed:
        raise RuntimeError("Seed is required")
    model_id = model.get_model_id()
    if not key:
        key = str(uuid.uuid4())
        execution = Execution(model_id=model_id,
                        prompt_version=prompt_version,
                        key=key)
        execution.messages.append(
                {
                    "role": "user",
                    "content": [
                        {"text": seed}
                    ]
                }
            )
    else:
        # jira key exists
        execution = store.get(key=key)
        if not execution:
            execution = Execution(model_id=model_id,
                        prompt_version=prompt_version,
                        key=key)
            
        execution.messages.append(
            {
                "role": "user",
                "content": [
                    {"text": seed}
                ]
            }
        )

    execution.start()

    total_itr_str = os.getenv("MAX_ITERATIONS")
    total_itr = int(total_itr_str) if total_itr_str is not None else 5


    while total_itr > execution.model_calls:
        execution.model_calls += 1
        try:
            api_response = bedrock_client.call_converse_api(execution.model_id, 
                                                            get_system_prompt(execution=execution),
                                                            tools,
                                                            execution.messages)
            recordMetrics(api_response, execution=execution)

            assistant_message = api_response["output"]["message"]
            execution.messages.append(assistant_message)

            # Check if assistant asked to use a tool
            tool_use_blocks = [
                c["toolUse"] for c in assistant_message["content"] if "toolUse" in c
            ]

            if not tool_use_blocks or assistant_message["content"][0]['text'] == "":
                break

            # For each tool request, execute and append result
            for tool_use_block in tool_use_blocks:
                tool_result_msg = handle_tool_use(execution=execution, tool_use_block=tool_use_block)
                execution.messages.append(tool_result_msg)
        except Exception as e:
            error = {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            execution.error = error
            execution.conclude()
            store.save(execution=execution)
            raise

    
    execution.conclude()
    store.save(execution=execution)
    return execution