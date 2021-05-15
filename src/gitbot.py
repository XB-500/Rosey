
if __name__ == "__main__":
    from mabel.utils.entropy import random_string
    branch_name = 'rosey-' + random_string()
    print(branch_name)

if __name__ == "__main__":

    import os
    import glob
    from mabel.utils.entropy import random_string
    from internals.adapters.http import HttpAdapter, GetRequestModel
    from internals.adapters.github import GitHubAdapter, GitHubListReposModel

    import subprocess
    import shutil

    TEMPLATE_REPO = "wasure-template"

    shutil.rmtree('temp', ignore_errors=True)
    os.makedirs('temp', exist_ok=True)
    subprocess.call(f'git clone https://github.com/joocer/{TEMPLATE_REPO}.git', shell=True, cwd='temp')


    repos = GitHubListReposModel (
        auth_token=os.environ.get('GITHUB_TOKEN'),
        name='joocer'
    )

    repo_list = GitHubAdapter.list_repos(repos).json()
    for repo in repo_list:
        url = F"https://raw.githubusercontent.com/{repo.get('full_name')}/main/TEMPLATE"
        code, headers, content = HttpAdapter.get(GetRequestModel(url=url))
        content = content.decode().strip()
        if code == 200 and content.startswith(f"https://github.com/joocer/{TEMPLATE_REPO}"):

            branch_name = 'rosey-' + random_string()
            print(branch_name)

            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)
            subprocess.call(F"git clone {repo.get('git_url')}", shell=True, cwd='temp')

            # open a '.templateignore'
            source_repo = glob.glob(f'temp/{TEMPLATE_REPO}/**')
            source_repo = [f[:len(f'temp/{TEMPLATE_REPO}/')] for f in source_repo]
            target_repo = glob.glob(f'temp/{repo.get("name")}')
            target_repo = [f[:len(f'temp/{repo.get("name")}')] for f in source_repo]

            for path in source_repo:

                print(f"looking at file {path}")

                with open(f'{TEMPLATE_REPO}/{path}', 'rb') as f:
                    source_file_contents = f.read()

                if path not in target_repo:
                    print(f'I need to add file {path}')
                

            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)
