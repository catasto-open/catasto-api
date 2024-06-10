import httpx


# a minimal alternative
def get_client():
    base_url = "" # os.environ["JUPYTERHUB_API_URL"]
    token = "" # os.environ["JUPYTERHUB_API_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(base_url=base_url, headers=headers)

def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item
