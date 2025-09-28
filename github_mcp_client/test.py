from client import GitHubMCPClient;
import json

client = GitHubMCPClient(
    github_token=""
)

client.start()
client.initialize()
client.send_initialized()

try:
    

    # sql = """
    # SELECT * FROM user_application 
    # WHERE application_id = '73cf1862-d084-4347-abf8-ad7e1386dc90'
    # ORDER BY created_at DESC
    # """

    # result = client.execute_search(
    #         index="logs-2025-09-07",query_body={"query": {"term": {"mdc.trace_id.keyword": "a7ae6d72be46823630571023f1dd027b"}}, "_source": ["message", "level", "@timestamp"], "size": 10}
    #     )

    # result = client.execute_search(
    #     index="my_index",
    #     query_body={"query": {"match_all": {}}}
    # )

    # result = client.execute_search(
    #     index="logs-2025-09-07",
    #     query_body={
    #         "query": {
    #             "term": {
    #                 "mdc.trace_id.keyword": "a7ae6d72be46823630571023f1dd027b"
    #             }
    #         },
    #         "_source": ["message", "level", "@timestamp"],
    #         "size": 10
    #     }
    # )

    # self,
    #     owner,
    #     repo,
    #     title,
    #     body=None,
    #     assignees=None,
    #     labels=None,
    #     milestone=None
    # result = client.list_tools_all()
    # {
    #         "owner": owner,
    #         "repo": repo,
    #         "issueNumber": issueNumber,
    #     }
    result = client.assign_copilot_to_issue("pAyzapp","turbo-onboarding-service","dummy issue through github mcp server","testing github-mcp-server")
    print(f"\n\n###########\n\n\n{json.dumps(result)}\n\n########")
finally:
    client.stop(force=True)