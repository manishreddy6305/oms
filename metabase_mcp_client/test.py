from client import MetabaseMCPClient;
import json

client = MetabaseMCPClient(
    metabase_url="http://host.docker.internal:3000",
    api_key="mb_ChJvd0OEifG9dkDLWNXWzFydc6yqXigqIiFRz15ch44="
)

client.start()

try:
    tools = client.list_tools()
    print("Available tools:", tools)

    sql = """
    SELECT * FROM user_application 
    WHERE application_id = '73cf1862-d084-4347-abf8-ad7e1386dc90'
    ORDER BY created_at DESC
    """
    result = client.execute_query(database_id=2, query=sql)
    print(f"\n\n###########\n\n\n{json.dumps(result)}\n\n########")
finally:
    client.stop(force=True)