import httpx


# a minimal alternative
def get_client():
    base_url = "" # os.environ["JUPYTERHUB_API_URL"]
    token = "" # os.environ["JUPYTERHUB_API_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(base_url=base_url, headers=headers)