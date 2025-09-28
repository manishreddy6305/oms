import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_router import MCPRouter
from utils import file_utils

class MistralLarge:
    def __init__(self):
        mcpRouter = MCPRouter()


    def get_model_id(self) :
        return "mistral.mistral-large-2402-v1:0"

    def get_system_prompt(self):
        DATABASE_SCHEMA_JSON = file_utils.read_json_file("../static/schemas.json")
        # Add examples for models context
        prompt = f"""You are an AI agent specialized in SQL query generation. 
            Schema:
            {DATABASE_SCHEMA_JSON}
        """

        return prompt


"""
V1 Prompt: 
        DATABASE_SCHEMA_JSON = file_utils.read_json_file("../static/schemas.json")
        OUTPUT_COMMAND_SCHEMA = file_utils.read_json_file("../static/command.json")
        # Add examples for models context
        return f
            You are an AI agent specialized in SQL query generation. 

            Your role and instructions:
            - Understand the user’s request in natural language.
            - Use the provided database schema to generate a valid SQL query to fetch the required data
            - Choose the correct database_id, table(s), and columns.
            - Always respect the column names and possible values as given in the schema.
            - Do not assume columns or tables that are not present in the schema.
            - Use LIMIT when appropriate if the user asks for “latest”, “top”, or “example”.
            - Output format must always be in json in below format. Strictly follow this format
            {OUTPUT_COMMAND_SCHEMA}

            Schema:
            {DATABASE_SCHEMA_JSON}



"""