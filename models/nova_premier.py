import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_router import MCPRouter
from utils import file_utils

class NovaPremier:
    def __init__(self):
        pass

    def get_model_id(self) :
        return "arn:aws:bedrock:us-east-1:019233110835:inference-profile/us.amazon.nova-premier-v1:0"