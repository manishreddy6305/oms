
from dotenv import load_dotenv
from client import JiraMCPClient
import os
import json

load_dotenv()

JIRA_URL=os.getenv("JIRA_URL")
JIRA_USERNAME=os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN=os.getenv("JIRA_API_TOKEN")



client = JiraMCPClient(
    site=JIRA_URL,
    email=JIRA_USERNAME,
    token=JIRA_API_TOKEN
)

client.start()
print(f"1. \n\n\n\n\n\n {client.initialize()} \n\n\n\n\n")
print(f"2. \n\n\n\n\n\n {client.send_initialized()} \n\n\n\n\n")
print(f"3. \n\n\n\n\n\n {json.dumps(client.get_issue(issue_key="TRC-28655"))} \n\n\n\n\n")



"""

[
  {
    "id": 41,
    "name": "Blocked"
  },
  {
    "id": 71,
    "name": "Rejected"
  },
  {
    "id": 21,
    "name": "Peer Review"
  }
]

"""

#  assignee = currentUser() AND priority=P1 ANd "Dev-ETA[Date]"="2025-07-02"

# try:
#     print("doint it now")
#     tools = client.get_issue(issue_id="TRC-10000")
#     print("Available tools:", tools)

#     #result = client.execute_query(database_id=2, query=sql)
#     #print(json.dumps(result))
# finally:
#     client.stop(force=True)