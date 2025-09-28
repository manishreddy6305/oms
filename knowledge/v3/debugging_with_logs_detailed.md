## "logs" / "logs-*" index log fields
1. timestamp: ISO instant
2. app: Emitting service (e.g. turbo-provisioning). Can be also identified by the service field. 
3. clusterName: Kubernetes cluster for the app(e.g. turboonboarding)
4. pod / host: pod id (useful for container logs deeper dive)
5. level: INFO / WARN / ERROR
6. mdc.trace_id: Correlates the entire provisioning flow
7. baggage#flow_name: Flow name if a unique to each endpoint written in service. It consists of parts such as cluster followed by app fllowed by api pseudo name.
8. parsedMessage.title: The title of the logs. 
9. parsedMessage.attributes.stackTrace: Exception stack trace (if present)
10. parsedMessage.attributes.message: Error detail / contextual message
stacktraces, exceptions etc.



## "ingress" index log fields
1. timestamp: ISO instant. e.g. Sep 13, 2025 @ 12:59:42.242
2. flow_name: Flow name if a unique to each endpoint written in service. It consists of parts such as cluster followed by app fllowed by api pseudo name.
3. http_user_agent
4. method: HTTP method
5. olympus_trace_id: distributed tracing trace id
6. response_code
7. response_time
8. service: The app/service name owning the current request logged by ingress
9. uri: Endpoint that's being invoked.
10. upstream_uri: Upstream uri which internally invoked current uri.




## Debugging Process
1. Search "ingress" index with based on endpoint e.g."uri: *application_id*" or with endpoint "uri: *issueBundle*", or with service name "service: "turbo-sourcing"". Strictly limit the logs under 10 unless you want to analyze the full trace.
2. Fetch the olympus_trace_id field from the ingress log. 
3. Query "logs" index with mdc.trace_id = olympus_trace_id. This will return the logs emitted by sevice including any stacktraces, downstreams responses, etc. Strictly limit the logs under 10 unless you want to analyze the full flow.

### Point to Note
1. Get minimal precise slice (avoid huge wildcard scans) use timestamps whenever possible.


### Examples

#### fetch logs with execute_elasticsearch_query tools

1. Search with application id in ingress logs "uri" which is nothing but the api path.
```json
{
    "index": "ingress-cluster",
    "body": {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "uri": "*2c831ee8-80f3-42ff-94ba-dc0b41aad205*"
                        }
                    }
                ]
            }
        },
        "size": 5
    }
}
```

1. Search with any field(span_id here) in "log-*" index
```json
{
    "index": "ingress-cluster",
    "body": {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "mdc.trace_id": "01b1caa36aaa042e"
                        }
                    }
                ]
            }
        },
        "size": 5
    }
}
``` 