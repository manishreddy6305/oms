import subprocess
import json
import time


class JiraMCPClient:
    def __init__(self,
                 site=None,
                 email=None,
                 token=None,
                 confluence_site=None,
                 confluence_email=None,
                 confluence_token=None,
                 image="mcp/atlassian:latest",
                 transport="stdio",
                 port=9001):
        self.image = image
        self.site = site
        self.email = email
        self.token = token
        self.confluence_site = confluence_site
        self.email = email
        self.confluence_email = confluence_email
        self.confluence_token = confluence_token
        self.transport = transport
        self.port = port
        self.base_url = f"http://localhost:{port}/mcp"
        self.proc = None

    def initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "jira-mcp-client",
                    "version": "0.1"
                }
            }
        }
        return self._send_stdio_request(req)
    
    def send_initialized(self):
        # just send, don't expect a response
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        self.proc.stdin.write(json.dumps(notif) + "\n")
        self.proc.stdin.flush()


    def start(self):
        envs = [
            "-e", f"JIRA_URL={self.site}",
            "-e", f"JIRA_USERNAME={self.email}",
            "-e", f"JIRA_API_TOKEN={self.token}",
            "-e", f"CONFLUENCE_URL={self.confluence_site}",
            "-e", f"CONFLUENCE_USERNAME={self.confluence_email}",
            "-e", f"CONFLUENCE_API_TOKEN={self.confluence_token}"
        ]

        if self.transport == "stdio":
            cmd = ["docker", "run", "-i", "--rm"] + envs + [self.image, "--transport", "stdio", "-v"]

            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        else:
            # fallback to HTTP
            cmd = ["docker", "run", "-i", "--rm", "-p", f"{self.port}:{self.port}"] \
                  + envs + [self.image, "--transport", "streamable-http", "--port", f"{self.port}", "-v"]

            self.proc = subprocess.Popen(cmd)

        time.sleep(3)  # allow server to start

    def stop(self, force=False):
        if not self.proc:
            return
        if force:
            self.proc.kill()
        else:
            self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
            self.proc.wait()

    # ------------------------
    # stdio request handling
    # ------------------------
    def _send_stdio_request(self, request):
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        response_line = self.proc.stdout.readline().strip()
        return json.loads(response_line)

    # ------------------------
    # tool methods
    # ------------------------
    def list_tools(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        return self._send_stdio_request(req) if self.transport == "stdio" else None

    def get_projects(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "jira_get_projects", "arguments": {}}
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)

    def get_issue(self, issue_key):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "jira_get_issue", "arguments": {"issue_key": issue_key}}
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)

    def jira_add_comment(self, issue_key: str, comment: str):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "jira_add_comment",
                "arguments": {
                    "issue_key": issue_key,
                    "comment": comment
                }
            }
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)

    def jira_get_transitions(self, issue_key: str):
        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "jira_get_transitions",
                "arguments": {
                    "issue_key": issue_key
                }
            }
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)


    def jira_search(self, jql: str, expand: str = None, fields: str = None, 
                limit: int = None, projects_filter: str = None, start_at: int = None):
        args = {"jql": jql}
        if expand:
            args["expand"] = expand
        if fields:
            args["fields"] = fields
        if limit:
            args["limit"] = limit
        if projects_filter:
            args["projects_filter"] = projects_filter
        if start_at is not None:
            args["start_at"] = start_at

        req = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "jira_search",
                "arguments": args
            }
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)
    

    def jira_update_issue(self, issue_key: str, fields: dict, 
                      additional_fields: dict = None, attachments: str = None):
        args = {
            "issue_key": issue_key,
            "fields": fields
        }
        if additional_fields:
            args["additional_fields"] = additional_fields
        if attachments:
            args["attachments"] = attachments

        req = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "jira_update_issue",
                "arguments": args
            }
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)
    
    def confluence_create_page(self, content: str, space_key: str, title: str, parent_id: str = None):
        args = {
            "content": content,
            "space_key": space_key,
            "title": title
        }
        if parent_id:
            args["parent_id"] = parent_id

        req = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "confluence_create_page",
                "arguments": args
            }
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)
    
    def confluence_update_page(self, content: str, title: str, page_id: str):
        args = {
            "content": content,
            "title": title,
            "page_id": page_id,
        }

        req = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "confluence_update_page",
                "arguments": args,
            },
        }
        res = self._send_stdio_request(req) if self.transport == "stdio" else None
        raw_text = res["result"]["content"][0]["text"]
        return json.loads(raw_text)




