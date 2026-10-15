
import httpx
# Patch Client.request which is used by most httpx methods
_orig_client_request = httpx.Client.request
def _patched_client_request(self, method, url, **kwargs):
    if 'proxies' in kwargs: del kwargs['proxies']
    return _orig_client_request(self, method, url, **kwargs)
httpx.Client.request = _patched_client_request

# Patch top-level functions
_orig_request = httpx.request
def _patched_request(method, url, **kwargs):
    if 'proxies' in kwargs: del kwargs['proxies']
    return _orig_request(method, url, **kwargs)
httpx.request = _patched_request

_orig_post = httpx.post
def _patched_post(url, **kwargs):
    if 'proxies' in kwargs: del kwargs['proxies']
    return _orig_post(url, **kwargs)
httpx.post = _patched_post

_orig_get = httpx.get
def _patched_get(url, **kwargs):
    if 'proxies' in kwargs: del kwargs['proxies']
    return _orig_get(url, **kwargs)
httpx.get = _patched_get

from youtubesearchpython import VideosSearch
try:
    videosSearch = VideosSearch('Lut le gaya', limit=1)
    result = videosSearch.result()
    if result and 'result' in result and len(result['result']) > 0:
        video = result['result'][0]
        print(f"Keys: {video.keys()}")
        print(f"Link: {video.get('link')}")
    else:
        print(f"Search results empty/invalid: {result}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
