from client import ElasticsearchMCPClient;
import json
import os 
from dotenv import load_dotenv

load_dotenv()

ES_URL=os.getenv("ES_URL")
ES_API_TOKEN=os.getenv("ES_API_TOKEN")


client = ElasticsearchMCPClient(
    es_url=ES_URL,
    api_key=ES_API_TOKEN
)

client.start()
client.initialize()
client.send_initialized()

try:
    

    sql = """
    SELECT * FROM user_application 
    WHERE application_id = '73cf1862-d084-4347-abf8-ad7e1386dc90'
    ORDER BY created_at DESC
    """

    # result = client.execute_search(
    #         index="logs-2025-09-07",query_body={"query": {"term": {"mdc.trace_id.keyword": "a7ae6d72be46823630571023f1dd027b"}}, "_source": ["message", "level", "@timestamp"], "size": 10}
    #     )

    query_body = {
    "query": {
        "bool": {
            "must": [
                {"match": {"mdc.span_id": "01b1caa36aaa042e"}}
            ],
            # "filter": [
            #     {"range": {"timestamp": {"gte": "now-1m"}}}
            # ]
        }

    },
        "size": 5
    }

    resp = client.execute_search("logs-service", query_body)

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


    # result = client.list_tools_all()
    #result = client.execute_search(database_id=2, query=sql)
    print(f"\n\n###########\n\n\n{json.dumps(resp)}\n\n########")
finally:
    client.stop(force=True)