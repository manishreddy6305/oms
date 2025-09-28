# Metabase MCP Client Example

## Prerequisites

1. **Run Metabase MCP**  
   Pull and start the [`mcp/metabase`](https://hub.docker.com/r/mcp/metabase) Docker image:
   ```bash
   docker run -d -p 8000:8000 mcp/metabase
   ```
2. **Run Metabase**
   Pull and start the official [`metabase/metabase`](https://hub.docker.com/r/metabase/metabase) Docker image:
    ```bash
    docker run -d -p 3000:3000 metabase/metabase
   ```
3. **Obtain an API Key**
   From your Metabase instance (http://localhost:3000), generate an API key under  
   **Admin → Settings → API Keys.**



## Example Usage
```python
from metabase_mcp_client.client import MetabaseMCPClient;
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
    print(json.dumps(result))
finally:
    client.stop(force=True)
```

## Sample Output
```json
[
    {
        "id": 1536,
        "application_id": "d4e3e3ae-d8c5-4550-8a3b-dd627e4d6046",
        "request_id": null,
        "section_name": "APPLICATION_CREATED",
        "mobile_number": "9915120387",
        "application_type": "INTERNAL",
        "created_at": "2025-09-01T22:44:17.205363Z",
        "updated_at": "2025-09-01T22:44:17.205363Z",
        "application_channel": "PAYZAPP"
    }
]
```