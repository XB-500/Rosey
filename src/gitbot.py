import os
import pathlib
from tempfile import TemporaryDirectory
from internals.adapters.github.github_adapter import GitHubFileModel, GitHubGroup


IGNORE = [
    f'.gitignore',
    f'README.md',
    f'requirements.txt',
    f'tests{os.sep}requirements.txt',
    f'src{os.sep}main.py',
    f'src{os.sep}config.json',
    f'TEMPLATE',
    f'LICENSE',
    f'NOTICE',
    f'src{os.sep}internals{os.sep}errors{os.sep}__init__.py',
    f'src{os.sep}internals{os.sep}flows{os.sep}__init__.py',
    f'src{os.sep}internals{os.sep}flows{os.sep}empty_flow.py',
    f'src{os.sep}internals{os.sep}models{os.sep}__init__.py']


def get_all_files(path='.', pattern='**/*'):
    files=[]
    file_refs = pathlib.Path(path).rglob(pattern)
    for file in file_refs:
        files.append(str(file))
    return files

if __name__ == "__main__":

    import os
    import pathlib
    import datetime
    from mabel.utils.entropy import random_string
    from mabel.logging import get_logger, set_log_name
    from internals.adapters.github import GitHubAdapter, GitHubListReposModel, GitHubFileModel

    import subprocess
    import shutil

    BOT_NAME = "rosey"
    ORG_NAME = "mabel-dev"
    TEMPLATE_REPO = "container-template"
    set_log_name(BOT_NAME)
    AUTH = os.environ.get('GITHUB_TOKEN')
    get_logger().setLevel(5)

    tempory_folder = TemporaryDirectory(prefix=BOT_NAME)
    template_path = pathlib.Path(tempory_folder.name) / TEMPLATE_REPO

    print(tempory_folder.name)
    subprocess.run(f'git clone https://{AUTH}@github.com/{ORG_NAME}/{TEMPLATE_REPO}.git', shell=True, cwd=tempory_folder.name, stdout=subprocess.DEVNULL)

    source_repo = get_all_files(template_path)
    source_repo = [f[len(f'{template_path}/'):] for f in source_repo]
    source_repo = [f for f in source_repo if not f.startswith('.git' + os.sep)]

    repos = GitHubListReposModel (
        authentication_token=AUTH,
        name=ORG_NAME,
        classification=GitHubGroup.orgs
    )

    repo_list = GitHubAdapter.list_repos(repos).json()
    get_logger().info(F"I found {len(repo_list)} repositories")
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
            get_logger().info(F"`{THIS_REPO}` appears to be based on `{TEMPLATE_REPO}`")

            # does the repo already have a bot branch?
            branches = GitHubAdapter.get_branches(ORG_NAME, THIS_REPO, AUTH)

            if any(True for branch in branches if branch.get('ref').startswith(f'refs/heads/{BOT_NAME}')):
                get_logger().error(f"`{THIS_REPO}` already has a branch created by `{BOT_NAME}`")
                continue

            branch_name = f'{BOT_NAME}-{datetime.datetime.now().strftime("%Y%m%d")}-{random_string(length=8)}'
            created_branch = False

            branch_path = pathlib.Path(tempory_folder.name) / THIS_REPO
            authenticated_url = repo.get('clone_url', '').replace('https://', f'https://{AUTH}@')
            subprocess.run(F"git clone {authenticated_url}", shell=True, cwd=tempory_folder.name, stdout=subprocess.DEVNULL)
            os.chdir(branch_path)

            target_repo = get_all_files(branch_path)
            target_repo = [f[len(f'{branch_path}/'):] for f in target_repo]

            for path in source_repo:

                message = f"path: {path} "

                if path in IGNORE:
                    get_logger().debug(message + 'ignoring')
                    continue

                if (template_path / path).is_file():

                    if not (branch_path / path).exists():
                        get_logger().debug(message + 'is new')
                        if not created_branch:
                            subprocess.run(F"git checkout -b {branch_name}", shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                            created_branch = True
                        os.makedirs((branch_path / path).parent, exist_ok=True)
                        shutil.copy2(template_path / path, branch_path / path)
                        subprocess.run(F'git add "{path}"', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                    else:
                        with open(template_path / path, 'rb') as f:
                            source_file_contents = f.read()
                        with open(branch_path / path, 'rb') as f:
                            target_file_contents = f.read()
                        if source_file_contents != target_file_contents:
                            get_logger().debug(message + 'needs to be updated')
                            if not created_branch:
                                subprocess.run(F"git checkout -b {branch_name}", shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                                created_branch = True
                            os.makedirs((branch_path / path).parent, exist_ok=True)
                            shutil.copy2(template_path / path, branch_path / path)
                            subprocess.run(F'git add "{path}"', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                        else:
                            get_logger().debug(message + 'needs no action')

                else:
                    get_logger().debug(message + "is not a file")

            if created_branch:

                subprocess.run(F'git config --global user.email "justin.joyce+rosey@joocer.com"', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run(F'git config --global user.name {BOT_NAME}', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run(F"git remote set-url origin {authenticated_url}", shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run(F"git remote set-url --push origin {authenticated_url}", shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run(F"git remote set-url --push origin {authenticated_url}", shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run('git commit -m "Syncing with Template"', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)
                subprocess.run(f'git push {authenticated_url} {branch_name}', shell=True, cwd=branch_path, stdout=subprocess.DEVNULL)


    os.chdir('../..')
    tempory_folder.cleanup()
