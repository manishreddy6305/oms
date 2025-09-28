import subprocess
import json

class MetabaseMCPClient:
    def __init__(self, metabase_url, api_key=None, image="mcp/metabase:latest"):
        self.metabase_url = metabase_url
        self.api_key = api_key
        self.image = image
        self.proc = None

    def start(self):
        envs = ["-e", f"METABASE_URL={self.metabase_url}"]
        envs += ["-e", f"METABASE_API_KEY={self.api_key}"]

        cmd = ["docker", "run", "-i", "--rm"] + envs + [self.image]

        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def stop(self, force=False):
        if self.proc:
            if force:
                self.proc.kill()   # sends SIGKILL
            else:
                self.proc.terminate()  # sends SIGTERM
            try:
                self.proc.wait(timeout=5)
            except Exception:
                # if still alive, hard kill
                self.proc.kill()
                self.proc.wait()

    def _send_request(self, request):
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        response_line = self.proc.stdout.readline().strip()
        return json.loads(response_line)

    def list_tools(self):
        # return self.list_tools_all() # Uncomment to list all tools
        return self.list_tools_required() 
        
    
    def list_tools_required(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        resp = self._send_request(req)
        all_tools = resp.get("result", {}).get("tools", [])

        query_tools = [
            t for t in all_tools if t["name"] in [
                "execute_query",
                "execute_card",
                "list_databases",
                "get_database_schema",
                "get_database_tables"
            ]
        ]
        return query_tools

    
    def list_tools_all(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        resp = self._send_request(req)
        return resp

    def execute_query(self, database_id, query, native_params=None):
        args = {"database_id": database_id, "query": query}
        if native_params:
            args["native_parameters"] = native_params

        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "execute_query", "arguments": args}
        }
        resp = self._send_request(req)
        raw_text = resp["result"]["content"][0]["text"]
        parsed = json.loads(raw_text)

        return self.format_metabase_result(parsed)
        
    def format_metabase_result(self, result):
        data = result["data"]
        rows = data["rows"]
        cols = [c["name"] for c in data["cols"]]

        formatted = [dict(zip(cols, row)) for row in rows]
        return formatted

