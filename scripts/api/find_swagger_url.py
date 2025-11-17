"""
Extract Swagger JSON URL from Swagger UI HTML page and JS files
"""
import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://10.10.100.100"

# Check init JS file
init_js_url = f"{base_url}/api/swagger/swagger/swagger-ui-init.js"
print(f"Checking: {init_js_url}")
try:
    r = requests.get(init_js_url, verify=False, timeout=10)
    js = r.text
    
    # Look for URL patterns
    patterns = [
        r'url["\']?\s*[:=]\s*["\']([^"\']+\.json)',
        r'spec["\']?\s*[:=]\s*["\']([^"\']+\.json)',
        r'["\']([^"\']*swagger[^"\']*\.json)',
        r'["\']([^"\']*openapi[^"\']*\.json)',
        r'/([^"\']*\.json)',
    ]
    
    found_urls = set()
    for pattern in patterns:
        matches = re.findall(pattern, js, re.I)
        found_urls.update(matches)
    
    print("Found URLs in init.js:")
    for u in sorted(found_urls):
        print(f"  {u}")
        
    # Also try to extract the full URL
    full_url_patterns = [
        r'https?://[^"\']+\.json',
        r'["\']([^"\']+/[^"\']*\.json)',
    ]
    
    for pattern in full_url_patterns:
        matches = re.findall(pattern, js, re.I)
        if matches:
            print(f"\nFull URLs found:")
            for m in matches:
                print(f"  {m}")
                
except Exception as e:
    print(f"Error: {e}")

# Try common endpoints
print("\nTrying common endpoints:")
common_paths = [
    '/api/swagger/v1/swagger.json',
    '/swagger/v1/swagger.json',
    '/api/swagger/swagger.json',
    '/swagger/swagger.json',
]

for path in common_paths:
    test_url = base_url + path
    try:
        r = requests.get(test_url, verify=False, timeout=5)
        if r.status_code == 200:
            try:
                data = r.json()
                if 'swagger' in data or 'openapi' in data:
                    print(f"[SUCCESS] {test_url}")
                    print(f"  Title: {data.get('info', {}).get('title', 'N/A')}")
                    print(f"  Version: {data.get('info', {}).get('version', 'N/A')}")
                    break
            except:
                pass
        else:
            print(f"[{r.status_code}] {test_url}")
    except Exception as e:
        print(f"[ERROR] {test_url}: {e}")


