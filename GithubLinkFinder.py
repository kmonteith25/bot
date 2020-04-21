import requests
import rootpath
from bot import constants

path_to_project = rootpath.detect()


def find_base_url() -> str or bool:
    url = "https://api.github.com/users/" + constants.github_username.lower() + "/repos"
    header = {'Authorization': GH_API_TOKEN}
    request = requests.get(url, headers=header)
    data = request.json()
    for repo in data:
        if repo['name'].lower() == constants.github_repo.lower():
            return repo["html_url"]


def find_file_url(path: str) -> str or bool:
    header = {'Authorization': GH_API_TOKEN}
    response = requests.get("https://api.github.com/repos/" + constants.github_username + "/" +
                            constants.github_repo + "/contents" + path, headers=header)

    if str(response.status_code) == "200":
        data = response.json()
        return data["html_url"]
    else:
        return False
