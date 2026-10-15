import os
import requests

# ==============================
# GITHUB AUTOMATION
# ==============================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

def _get_headers():
    token = os.getenv("GITHUB_TOKEN")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

async def github_get_user_info() -> str:
    """
    Retrieves the authenticated user's information, including account name (login).
    """
    try:
        response = requests.get(f"{BASE_URL}/user", headers=_get_headers())
        if response.status_code == 200:
            user = response.json()
            return f"👤 GitHub Account: {user['login']}\nName: {user.get('name', 'N/A')}\nPublic Repos: {user.get('public_repos')}\nFollowers: {user.get('followers')}"
        else:
            return f"❌ Failed to get user info: {response.status_code} {response.text}"
    except Exception as e:
        return f"❌ Error: {e}"

async def github_list_repositories(limit: int = 20) -> str:
    """
    Lists the names of the authenticated user's repositories.
    """
    try:
        response = requests.get(f"{BASE_URL}/user/repos?sort=updated&per_page={limit}", headers=_get_headers())
        if response.status_code == 200:
            repos = response.json()
            if not repos:
                return "No repositories found."
            repo_list = [r['name'] for r in repos]
            return "📁 Repositories:\n" + "\n".join(repo_list)
        else:
            return f"❌ Failed to list repos: {response.status_code} {response.text}"
    except Exception as e:
        return f"❌ Error: {e}"

async def github_get_repo_count() -> str:
    """
    Returns the total number of repositories for the authenticated user.
    """
    try:
        response = requests.get(f"{BASE_URL}/user", headers=_get_headers())
        if response.status_code == 200:
            user = response.json()
            total = user.get('public_repos', 0) + user.get('total_private_repos', 0)
            return f"📊 You have a total of {total} repositories."
        else:
            return f"❌ Failed to get repo count: {response.status_code} {response.text}"
    except Exception as e:
        return f"❌ Error: {e}"

async def github_create_repository(name: str, description: str = "", private: bool = False) -> str:
    """
    Creates a new repository on GitHub.
    """
    try:
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        response = requests.post(f"{BASE_URL}/user/repos", headers=_get_headers(), json=data)
        if response.status_code == 201:
            repo = response.json()
            return f"✅ Repository '{name}' created successfully!\nURL: {repo['html_url']}"
        else:
            return f"❌ Failed to create repo: {response.status_code} {response.text}"
    except Exception as e:
        return f"❌ Error: {e}"

async def github_delete_repository(owner: str, repo_name: str) -> str:
    """
    Deletes a repository on GitHub. Requires admin permissions.
    """
    try:
        response = requests.delete(f"{BASE_URL}/repos/{owner}/{repo_name}", headers=_get_headers())
        if response.status_code == 204:
            return f"✅ Repository '{repo_name}' deleted successfully."
        else:
            return f"❌ Failed to delete repo: {response.status_code} {response.text}"
    except Exception as e:
        return f"❌ Error: {e}"
