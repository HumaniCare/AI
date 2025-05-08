import json
import re


def extract_json_from_content(content):
    match = re.search(r"\{[\s\S]*\}", content)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            print("JSON 파싱 실패:", e)
            return {}
    else:
        print("JSON 형태가 아님")
        return {}
