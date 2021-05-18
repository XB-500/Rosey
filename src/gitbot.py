
from internals.adapters.github.github_adapter import GitHubFileModel, GitHubGroup

IGNORE = ['README.md', 'requirements.txt', 'src\\main.py', 'src\\config.json', 'TEMPLATE', 'LICENSE', 'NOTICE']

if __name__ == "__main__":

    import os
    import glob
    from mabel.utils.entropy import random_string
    from mabel.logging import get_logger, set_log_name
    from internals.adapters.http import HttpAdapter, GetRequestModel
    from internals.adapters.github import GitHubAdapter, GitHubListReposModel, GitHubFileModel

    import subprocess
    import shutil

    ORG_NAME = "mabel-dev"
    TEMPLATE_REPO = "container-template"
    set_log_name("ROSEY")
    AUTH = os.environ.get('GITHUB_TOKEN')

    shutil.rmtree('temp', ignore_errors=True)
    os.makedirs('temp', exist_ok=True)
    subprocess.call(f'git clone https://github.com/{ORG_NAME}/{TEMPLATE_REPO}.git', shell=True, cwd='temp')


    repos = GitHubListReposModel (
        auth_token=AUTH,
        name=ORG_NAME,
        classification=GitHubGroup.orgs
    )

    repo_list = GitHubAdapter.list_repos(repos).json()
    get_logger().debug(F"found {len(repo_list)} repositories")
    for repo in repo_list:

        if repo['name'] == TEMPLATE_REPO:
            continue

        file = GitHubFileModel(
            file_path = "TEMPLATE",
            owner = ORG_NAME,
            repository_name = repo.get('name'),
            auth_token = AUTH
        )
        status, content = GitHubAdapter.get_file(file)
        content = content.decode().strip()
        print(status, content, repo.get('full_name'))
        if status == 200 and content.startswith(f"https://github.com/{ORG_NAME}/{TEMPLATE_REPO}"):
            get_logger().debug(F"`{repo.get('full_name')}` appears to be based on `{TEMPLATE_REPO}`")

            branch_name = 'rosey-' + random_string(length=16)

            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)
            authenticated_url = repo.get('clone_url', '').replace('https://', f'https://{AUTH}@')
            subprocess.call(F"git clone {authenticated_url}", shell=True, cwd='temp')

            source_repo = glob.glob(f'temp/{TEMPLATE_REPO}/**', recursive=True)
            source_repo = [f[len(f'temp/{TEMPLATE_REPO}/'):] for f in source_repo]
            target_repo = glob.glob(f'temp/{repo.get("name")}/**', recursive=True)
            target_repo = [f[len(f'temp/{repo.get("name")}'):] for f in target_repo]

            for path in source_repo:

                print(f"looking at path: {path}")

                if path in IGNORE:
                    print('ignoring')
                    continue

                if os.path.isfile(f'temp/{TEMPLATE_REPO}/{path}'):

                    if not os.path.exists(f'temp/{repo.get("name")}/{path}'):
                        print(f'I need to add file {path}')

                    else:
                        with open(f'temp/{TEMPLATE_REPO}/{path}', 'rb') as f:
                            source_file_contents = f.read()
                        with open(f'temp/{repo.get("name")}/{path}', 'rb') as f:
                            target_file_contents = f.read()
                        if source_file_contents != target_file_contents:
                            print(f'I need to update {path}')
                        else:
                            print(f'{path} is okay')
                

#            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)
