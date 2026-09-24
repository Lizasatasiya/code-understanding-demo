import urllib.request
import json

class ServerClient:
    def send(self, session_data: dict):
        print("[SERVER] Sending understanding session...")
        
        url = "http://127.0.0.1:8000/understanding-session"
        data = json.dumps(session_data).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("[SERVER] Session received successfully.")
                else:
                    print(f"[SERVER] Failed with status: {response.status}")
        except Exception as e:
            print(f"[SERVER] Error communicating with server: {e}")
            # Do not fail the commit if the server is just offline for the prototype
