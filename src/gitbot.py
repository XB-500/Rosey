
from typing import Optional
from tempfile import TemporaryDirectory

from requests.api import get
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

    template_folder = TemporaryDirectory(prefix='rosey')
    print(template_folder.name)
    print(subprocess.run(f'git clone https://github.com/{ORG_NAME}/{TEMPLATE_REPO}.git', shell=False, cwd=template_folder.name))

    repos = GitHubListReposModel (
        authentication_token=AUTH,
        name=ORG_NAME,
        classification=GitHubGroup.orgs
    )

    repo_list = GitHubAdapter.list_repos(repos).json()
    get_logger().debug(F"found {len(repo_list)} repositories")
    for repo in repo_list:

        THIS_REPO = repo['name']

        # is the repo the template repo?
        if THIS_REPO == TEMPLATE_REPO:
            continue

        file = GitHubFileModel(
            file_path = "TEMPLATE",
            owner = ORG_NAME,
            repository_name = THIS_REPO,
            authentication_token = AUTH
        )
        status, content = GitHubAdapter.get_file(file)
        content = content.decode().strip()

        if status == 200 and content.startswith(f"https://github.com/{ORG_NAME}/{TEMPLATE_REPO}"):
            get_logger().debug(F"`{THIS_REPO}` appears to be based on `{TEMPLATE_REPO}`")

            # does the repo already have a rosey branch?
            branches = GitHubAdapter.get_branches(ORG_NAME, THIS_REPO, AUTH)
            print(branches, type(branches))
            if any(True for branch in branches if branch.get('ref').startswith('refs/heads/rosey')):
                get_logger().debug(f"{THIS_REPO} already has a branch created by Rosey")
                continue

            branch_name = 'rosey-' + random_string(length=16)
            created_branch = False

            branch_folder = TemporaryDirectory(prefix='rosey')
            authenticated_url = repo.get('clone_url', '').replace('https://', f'https://{AUTH}@')
            subprocess.run(F"git clone {authenticated_url}", shell=False, cwd=branch_folder.name)
            os.chdir(f'{branch_folder.name}/{THIS_REPO}')

            source_repo = glob.glob(f'{template_folder.name}/**', recursive=True)
            source_repo = [f[len(f'{template_folder.name}/{TEMPLATE_REPO}/'):] for f in source_repo]
            target_repo = glob.glob(f'{branch_folder.name}/**', recursive=True)
            target_repo = [f[len(f'{branch_folder.name}/{THIS_REPO}/'):] for f in target_repo]

            for path in source_repo:

                print(f"path: {path} ", end='')

                if path in IGNORE:
                    print('ignoring')
                    continue

                if os.path.isfile(f'{template_folder.name}/{TEMPLATE_REPO}/{path}'):

                    if not os.path.exists(f'{branch_folder.name}/{THIS_REPO}/{path}'):
                        print(f'is not in repo')
                        if not created_branch:
                            subprocess.run(F"git checkout -b {branch_name}", shell=True, cwd=f'{branch_folder.name}{THIS_REPO}')
                            created_branch = True
                        shutil.copy2(f'{template_folder.name}/{TEMPLATE_REPO}/{path}', f'{branch_folder.name}/{THIS_REPO}/{path}')
                        subprocess.run(F'git add "{path}"', shell=False, cwd=f'{branch_folder.name}/{THIS_REPO}')
                    else:
                        with open(f'{template_folder.name}/{TEMPLATE_REPO}/{path}', 'rb') as f:
                            source_file_contents = f.read()
                        with open(f'{branch_folder.name}/{THIS_REPO}/{path}', 'rb') as f:
                            target_file_contents = f.read()
                        if source_file_contents != target_file_contents:
                            print('needs to be updated')
                            if not created_branch:
                                subprocess.run(F"git checkout -b {branch_name}")
                                created_branch = True
                            shutil.copy2(f'{template_folder.name}/{TEMPLATE_REPO}/{path}', f'{branch_folder.name}/{THIS_REPO}/{path}')
                            subprocess.run(F'git add "{path}"', shell=False, cwd=f'{branch_folder.name}/{THIS_REPO}')
                        else:
                            print(f'okay')

                else:
                    print("not a file")

            if created_branch:

                subprocess.run('git commit -m "Syncing with Template"', shell=False, cwd=f'{branch_folder.name}/{THIS_REPO}')
                subprocess.run(f'git push origin {branch_name}', shell=False, cwd=f'{branch_folder.name}/{THIS_REPO}')

                quit()

            os.chdir('../..')
            branch_folder.cleanup()

    template_folder.cleanup()
