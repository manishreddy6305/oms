import time

import time

class Execution:
    def __init__(self, model_id, prompt_version, key):
        self.model_id = model_id
        self.prompt_version = prompt_version
        self.messages = []
        self.input_token = []
        self.output_tokens = []
        self.model_latencies = []
        self.mcp_calls = []
        self.model_calls = 0
        self.key = key
        self.timeline = []
        self.start_time = time.time()
        self.end_time = time.time()
        self.error = None

    def start(self):
        self.start_time = time.time()
        self.end_time = self.start_time

    def conclude(self):
        self.end_time = time.time()
        # record the segment
        self.timeline.append([self.start_time, self.end_time])


    # --- added methods ---
    def to_dict(self):
        return {
            "model_id": self.model_id,
            "prompt_version": self.prompt_version,
            "messages": self.messages,
            "input_token": self.input_token,
            "output_tokens": self.output_tokens,
            "model_latencies": self.model_latencies,
            "mcp_calls": self.mcp_calls,
            "model_calls": self.model_calls,
            "timeline": self.timeline,
            "key": self.key,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: dict):
        inst = cls(
            model_id=data.get("model_id"),
            prompt_version=data.get("prompt_version"),
            key=data.get("key"),
        )
        inst.messages = data.get("messages", [])
        inst.input_token = data.get("input_token", [])
        inst.output_tokens = data.get("output_tokens", [])
        inst.model_latencies = data.get("model_latencies", [])
        inst.mcp_calls = data.get("mcp_calls", [])
        inst.model_calls = data.get("model_calls", 0)
        inst.timeline = data.get("timeline", [])
        inst.start_time = data.get("start_time", inst.start_time)
        inst.end_time = data.get("end_time", inst.end_time)
        return inst
   