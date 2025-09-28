import subprocess
import json


class GitHubMCPClient:
    def __init__(self, github_token, image="mcp/github-mcp-server"):
        self.github_token = github_token
        self.image = image
        self.proc = None

    def start(self):
        envs = ["-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}"]
        envs += ["-e", "GITHUB_TOOLSETS=all"]
        cmd = ["docker", "run", "-i", "--rm"] + envs + [self.image]
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
                    "name": "github-mcp-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": True
                }
            }
        }
        return self._send_request(req)

    def list_tools_all(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        return self._send_request(req)

    def list_tools_required(self):
        resp = self.list_tools_all()
        all_tools = resp.get("result", {}).get("tools", [])
        
        github_tools = [
            t for t in all_tools if t["name"] in [
                "create_issue",
                "assign_copilot_to_issue",
            ]
        ]
        return github_tools

    def create_issue(
        self,
        owner,
        repo,
        title,
        body=None,
        assignees=None,
        labels=None,
        milestone=None
    ):
        args = {
            "owner": owner,
            "repo": repo,
            "title": title,
        }
        if body:
            args["body"] = body
        if assignees:
            args["assignees"] = assignees
        if labels:
            args["labels"] = labels
        if milestone is not None:
            args["milestone"] = milestone

        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "create_issue", "arguments": args},
        }
        return self._send_request(req)

    def assign_copilot_to_issue(self, owner, repo, issueNumber):
        args = {
            "owner": owner,
            "repo": repo,
            "issueNumber": issueNumber,
        }
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "assign_copilot_to_issue", "arguments": args},
        }
        return self._send_request(req)
