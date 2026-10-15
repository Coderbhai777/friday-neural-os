
import httpx
import json

# Patch Client.request
_orig_client_request = httpx.Client.request
def _patched_client_request(self, method, url, **kwargs):
    if 'proxies' in kwargs: del kwargs['proxies']
    return _orig_client_request(self, method, url, **kwargs)
httpx.Client.request = _patched_client_request

from youtubesearchpython import VideosSearch
try:
    videosSearch = VideosSearch('Despacito', limit=1)
    result = videosSearch.result()
    print(json.dumps(result, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
