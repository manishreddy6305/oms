import os
import json
import sys

# Add parent directory to path to access utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import file_utils

class KnowledgeMCPClient:
    def __init__(self): 
        pass

    def get_knowledge(self, name, version):
        
        file_path = f"knowledge/{version}/{name}"
        
        # Use file_utils to handle the file path resolution consistently
        if file_path.endswith('.json'):
            return json.loads(file_utils.read_json_file(file_path))
        else:
            return {
                "text": file_utils.read_file(file_path)
            }
