import subprocess
import json


class ElasticsearchMCPClient:
    def __init__(self, es_url, api_key=None, ssl_skip_verify=True, image="mcp/elasticsearch:latest"):
            """
            es_url: The Elasticsearch endpoint that the MCP server inside Docker connects to.
            api_key: Optional API key if your MCP server expects it.
            verify_ssl: Whether to verify SSL certificates (set False for self-signed certs).
            image: Docker image for the Elasticsearch MCP server.
            """
            self.es_url = es_url
            self.api_key = api_key
            self.ssl_skip_verify = ssl_skip_verify
            self.image = image
            self.proc = None

    def start(self):
        envs = ["-e", f"ES_URL={self.es_url}"]
        if self.api_key:
            envs += ["-e", f"ES_API_KEY={self.api_key}"]
        envs += ["-e", f"ES_SSL_SKIP_VERIFY={str(self.ssl_skip_verify).lower()}"]
        cmd = ["docker", "run", "-i", "--rm"] + envs + [self.image, "stdio"]
        #print(f"cmd : {cmd}")
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def stop(self, force=False):
        if self.proc:
            if force:
                self.proc.kill()
            else:
                self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
                self.proc.wait()

    def _send_request(self, request):
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        response_line = self.proc.stdout.readline().strip()
        return json.loads(response_line)


    def send_initialized(self):
        notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self.proc.stdin.write(json.dumps(notif) + "\n")
        self.proc.stdin.flush()
        print("📨 Sent initialized notification")


    def initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1",
                "clientInfo": {
                    "name": "es-mcp-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": True
                }
            }
        }
        return self._send_request(req)
        

    def list_tools_required(self):
        """List only essential tools."""
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        resp = self._send_request(req)
        all_tools = resp.get("result", {}).get("tools", [])

        # Filter for query/search relevant tools
        query_tools = [
            t for t in all_tools if t["name"] in [
                "search",
                "esql",
                "get_mappings",
            ]
        ]
        return query_tools

    def list_tools_all(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        return self._send_request(req)

    def execute_search(self, index, query_body):
        
        args = {"index": index, "query_body": query_body}
        
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "search", "arguments": args},
        }
        resp = self._send_request(req)

        return self.convert_response_to_json(resp)
    
    def execute_esql(self, query):
        
        args = {"query": query}
        
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "esql", "arguments": args},
        }
        resp = self._send_request(req)

        return resp
    
    def execute_get_mapping(self, index):
        
        args = {"index": index}
        
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_mappings", "arguments": args},
        }
        resp = self._send_request(req)

        return resp
    def convert_response_to_json(self, resp):
        content_list = resp.get("result", {}).get("content", [])
        json_text = None
        for item in content_list:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Heuristic: check if it looks like JSON (starts with [ or {)
                if text.strip().startswith("[") or text.strip().startswith("{"):
                    json_text = text
                    break

        # Step 3: parse it
        if json_text:
            data = json.loads(json_text)
            truncated_data = self.truncate_fields(data)

            return truncated_data

        return {}

    def truncate_fields(self, obj, max_len=200):
        if isinstance(obj, dict):
            return {k: self.truncate_fields(v, max_len) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.truncate_fields(x, max_len) for x in obj]
        elif isinstance(obj, str):
            return obj if len(obj) <= max_len else obj[:max_len] + "..."
        else:
            return obj
