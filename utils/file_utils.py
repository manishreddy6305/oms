import json
import os

def read_json_file(file_path):
    abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        file_path.lstrip('../'))
    try:
        with open(abs_path, 'r') as file:
            data = json.load(file)
            return json.dumps(data)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")
    
def read_file(file_path):
    abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        file_path.lstrip('../'))
    try:
        with open(abs_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")