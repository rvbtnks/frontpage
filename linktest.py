#!/usr/bin/env python3
import requests

def main():
    host = input("Linkwarden URL (e.g. http://192.168.1.100:3000): ").strip().rstrip('/')
    api_key = input("API Key: ").strip()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        ("/api/v1/links", "Links"),
        ("/api/v1/collections", "Collections"),
        ("/api/v1/tags", "Tags"),
        ("/api/v1/dashboard", "Dashboard"),
    ]
    
    for endpoint, name in endpoints:
        print(f"\n{'='*60}")
        print(f"{name} - {endpoint}")
        print('='*60)
        
        try:
            resp = requests.get(f"{host}{endpoint}", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            if isinstance(data, dict) and 'response' in data:
                data = data['response']
            
            if isinstance(data, list):
                print(f"Got {len(data)} items")
                if data:
                    print(f"\nFirst item keys: {list(data[0].keys())}")
                    print(f"\nFirst item sample:")
                    for k, v in data[0].items():
                        preview = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
                        print(f"  {k}: {preview}")
            else:
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                if isinstance(data, dict):
                    for k, v in data.items():
                        preview = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
                        print(f"  {k}: {preview}")
                        
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
