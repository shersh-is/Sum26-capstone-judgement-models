import requests

VM_API_URL = "http://10.93.27.9"

def get_vm_status():
    try:
        r = requests.get(f"{VM_API_URL}/status", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": str(e)}
