from github_mcp_client.client import GitHubMCPClient
from metabase_mcp_client.client import MetabaseMCPClient
from jira_mcp_client.client import JiraMCPClient
from knowledge_mcp_client.client import KnowledgeMCPClient
from elasticsearch_mcp_client.client import ElasticsearchMCPClient
from objects.execution import Execution

import json
from dotenv import load_dotenv
import os

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
METABASE_URL = os.getenv("METABASE_URL")
METABASE_API_KEY = os.getenv("METABASE_API_KEY")
ES_URL=os.getenv("ES_URL")
ES_API_TOKEN=os.getenv("ES_API_TOKEN")
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")
CONFLUENCE_URL=os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME=os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN=os.getenv("CONFLUENCE_API_TOKEN")


class MCPRouter:
    def __init__(self):
        # Metabase Client
        self.metabaseMCPClient = MetabaseMCPClient(
            metabase_url=METABASE_URL,
            api_key=METABASE_API_KEY,
        )
        # Elasticsearch Client
        self.elasticSearchMCPClient = ElasticsearchMCPClient(
            es_url=ES_URL,
            api_key=ES_API_TOKEN,
            ssl_skip_verify=True,
        )
        
        self.metabaseMCPClient.start()
        
        self.elasticSearchMCPClient.start()
        self.elasticSearchMCPClient.initialize()
        self.elasticSearchMCPClient.send_initialized()

        # Jira Client
        self.jira_client = JiraMCPClient(
            site=JIRA_URL, email=JIRA_USERNAME, token=JIRA_API_TOKEN,
            confluence_site=CONFLUENCE_URL,confluence_email=CONFLUENCE_USERNAME,confluence_token=CONFLUENCE_API_TOKEN,
        )
        self.jira_client.start()
        self.jira_client.initialize()
        self.jira_client.send_initialized()
        self.knowledge_client = KnowledgeMCPClient()
        
        #GITHUB mcp client
        self.github_client = GitHubMCPClient(github_token = GITHUB_TOKEN)

        self.github_client.start()
        self.github_client.initialize()
        self.github_client.send_initialized()

    def execute_tool(self, execution: Execution, command):
        print(f"\n\nMCPROUTER: Executing tool with command: {command}")

        tool_name = command["tool_name"]
        params = command["params"]

        # Map tool_name → handler
        tool_map = {
            "execute_query": self.execute_query,
            "jira_add_comment": self.jira_add_comment,
            "jira_get_transitions": self.jira_get_transitions,
            "jira_get_issue": self.get_issue,
            "jira_update_issue": self.jira_update_issue,
            "get_knowledge": lambda p: self.get_knowledge(p, execution),
            "execute_elasticsearch_query": self.execute_elasticsearch_query,
            "esql": self.execute_esql,
            "get_mappings": self.execute_get_mapping,
            "create_issue": self.create_github_issue,
            "assign_copilot_to_issue": self.assign_copilot_to_issue,
            "confluence_create_page": self.confluence_create_page,
            "confluence_update_page": self.confluence_update_page
        }

        if tool_name not in tool_map:
            print(f"Unknown tool: {tool_name}")
            raise ValueError(f"Unknown tool: {tool_name}")

        # Execute the matching tool
        handler = tool_map[tool_name]
        res = handler(params)

        print(
            f"MCPROUTER: Executed tool with command: {json.dumps(command)} "
            f"\nand result\n{json.dumps(res)}\n\n"
        )
        return res

    def get_knowledge(self, params, execution: Execution):
        knowledge_name = params["name"]
        result = self.knowledge_client.get_knowledge(
            name=knowledge_name,
            version=execution.prompt_version
        )
        return result

    def get_tools(self, file_path="./static/tools.json"):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return json.dumps(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {file_path}")

    # -------------------------------
    # Metabase
    # -------------------------------
    def execute_query(self, params):
        database_id = params["database_id"]
        query = params["query"]

        result = self.metabaseMCPClient.execute_query(
            database_id=database_id, query=query
        )
        return result

    # -------------------------------
    # Jira
    # -------------------------------
    def jira_add_comment(self, params):
        issue_key = params["issue_key"]
        comment = params["comment"]
        return self.jira_client.jira_add_comment(issue_key, comment)

    def jira_get_transitions(self, params):
        issue_key = params["issue_key"]
        return self.jira_client.jira_get_transitions(issue_key)

    def jira_search(self, params):
        jql = params["jql"]
        expand = params.get("expand")
        fields = params.get("fields")
        limit = params.get("limit", 50)
        projects_filter = params.get("projects_filter")
        start_at = params.get("start_at", 0)

        return self.jira_client.jira_search(
            jql=jql,
            expand=expand,
            fields=fields,
            limit=limit,
            projects_filter=projects_filter,
            start_at=start_at,
        )
    def get_issue(self, params):

        return self.jira_client.get_issue(issue_key=params["issue_key"])

    def jira_update_issue(self, params):
        issue_key = params["issue_key"]
        fields = params["fields"]
        additional_fields = params.get("additional_fields")
        attachments = params.get("attachments")

        return self.jira_client.jira_update_issue(
            issue_key=issue_key,
            fields=fields,
            additional_fields=additional_fields,
            attachments=attachments,
        )

    def execute_elasticsearch_query(self,params):
        index = params["index"]
        body = params["body"]

        result = self.elasticSearchMCPClient.execute_search(
            index=index,query_body=body
        )
        return result

    def execute_esql(self, params):
        query = params["query"]

        result = self.elasticSearchMCPClient.execute_esql(
            query=query
        )
        return result

    def execute_get_mapping(self, params):
        index = params["index"]

        result = self.elasticSearchMCPClient.execute_get_mapping(
            index=index
        )
        return result
    
    def create_github_issue(self, params):
        owner = params["owner"]
        repo = params["repo"]
        title = params["title"]
        body = params["body"]
        
        result = self.github_client.create_issue(
            owner=owner,
            repo=repo,
            body=body,
            title=title
        )
        return result
    
    def assign_copilot_to_issue(self, params):
        issueNumber = params["issueNumber"]
        owner = params["owner"]
        repo = params["repo"]

        result = self.github_client.assign_copilot_to_issue(
            issueNumber=issueNumber,
            owner=owner,
            repo=repo,
        )
        return result
    
    def confluence_create_page(self, params):
        content = params["content"]
        space_key = params["space_key"]
        title = params["title"]
        parent_id = params.get("parent_id")

        return self.jira_client.confluence_create_page(
            content=content,
            space_key=space_key,
            title=title,
            parent_id=parent_id,
        )
        
    def confluence_update_page(self, params):
        content = params["content"]
        title = params["title"]
        page_id = params["page_id"]

        return self.confluence_client.confluence_update_page(
            content=content,
            title=title,
            page_id=page_id,
        )