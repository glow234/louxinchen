import requests
from datetime import datetime

def save_latest_reply(text, bin_id=None, access_key=None):
    if not bin_id or not access_key:
        return False

    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    data = {
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    
    try:
        response = requests.put(
            url,
            json=data,
            headers={
                "X-Access-Key": access_key,
                "Content-Type": "application/json"
            }
        )
        if response.status_code != 200:
            print(f"JSONBin Save Error: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"JSONBin Save Exception: {e}")
        return False

def get_latest_reply(bin_id=None, access_key=None):
    if not bin_id or not access_key:
        return {"has_new": False, "text": None}
    
    try:
        url = f"https://api.jsonbin.io/v3/b/{bin_id}/latest"
        response = requests.get(
            url,
            headers={"X-Access-Key": access_key}
        )
        if response.status_code == 200:
            data = response.json().get("record", {})
            if not data.get("read", False):
                data["read"] = True
                requests.put(
                    f"https://api.jsonbin.io/v3/b/{bin_id}",
                    json=data,
                    headers={"X-Access-Key": access_key}
                )
                return {"has_new": True, "text": data.get("text")}
        return {"has_new": False, "text": None}
    except:
        return {"has_new": False, "text": None}
