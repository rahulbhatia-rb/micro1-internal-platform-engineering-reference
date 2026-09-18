import json, sys
from dataclasses import asdict
from src.platform_contract import WorkloadRequest, build_plan
for line in sys.stdin:
    if line.strip():
        payload=json.loads(line)
        print(json.dumps({"request":payload,"plan":asdict(build_plan(WorkloadRequest(**payload)))}))
