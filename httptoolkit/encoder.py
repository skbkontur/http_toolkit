import json
import uuid
from typing import Any


class DefaultJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


def default_json_encoder(content: Any) -> str:
    return json.dumps(content, cls=DefaultJSONEncoder)
