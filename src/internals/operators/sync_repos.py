import os
import pathlib
import shutil
import datetime
import subprocess
from mabel import BaseOperator  # type:ignore
from mabel.utils.entropy import random_string  # type:ignore
from tempfile import TemporaryDirectory
from ..adapters.github import GitHubAdapter, GitHubListReposModel, GitHubGroup

DEFAULT_BOTIGNORE = [
    ".gitignore",
    ".github/workflows/formatter.yml",
    "README.md",
    "requirements.txt",
    "src/main.py",
    "src/config.json",
    "TEMPLATE",
    "src/internals/adapters/README.md",
    "src/internals/errors/__init__.py",
    "src/internals/errors/README.md",
    "src/internals/flows/__init__.py",
    "src/internals/flows/example_flow.py",
    "src/internals/flows/README.md",
    "src/internals/models/__init__.py",
    "src/internals/models/README.md",
    "src/internals/operators/__init__.py",
    "src/internals/operators/empty_operator.py",
    "src/internals/operators/README.md",
    "tests/README.md",
    "tests/requirements.txt",
]


def get_all_files(path=".", pattern="**/*"):
    files = []
    file_refs = pathlib.Path(path).rglob(pattern)
    for file in file_refs:
        files.append(str(file))
    return files


class SyncWithRepoOperator(BaseOperator):
    def __init__(self, auth_token, organization, source_repo, comments, **kwargs):

        super().__init__(**kwargs)

        self.AUTH_TOKEN = auth_token
        self.ORGANIZATION = organization
        self.source_repo = source_repo
        self.comments = comments

    def execute(self, data, context):
        THIS_REPO = data["name"]
        BOT_NAME = context["job_name"]

        temporary_folder = TemporaryDirectory(prefix=BOT_NAME)
        template_path = pathlib.Path(temporary_folder.name) / self.source_repo

        # does the repo already have a bot branch?
        branches = GitHubAdapter.get_branches(
            self.ORGANIZATION, THIS_REPO, self.AUTH_TOKEN
        )  # type:ignore

        if any(
            True
            for branch in branches
            if branch.get("ref").startswith(f"refs/heads/{BOT_NAME}")
        ):
            self.logger().error(
                f"`{THIS_REPO}` already has a branch created by `{BOT_NAME}`"
            )
            return None

        # clone the template repo
        subprocess.run(
            f"git clone https://{self.AUTH_TOKEN}@github.com/{self.ORGANIZATION}/{self.source_repo}.git",
            shell=True,
            cwd=temporary_folder.name,
            stdout=subprocess.DEVNULL,
        )
        source_repo = get_all_files(template_path)
        source_repo = [f[len(f"{template_path}/") :] for f in source_repo]
        source_repo = [f for f in source_repo if not f.startswith(".git" + os.sep)]

        # check out the target repo
        branch_path = pathlib.Path(temporary_folder.name) / THIS_REPO
        authenticated_url = data.get("clone_url", "").replace(
            "https://", f"https://{self.AUTH_TOKEN}@"
        )
        subprocess.run(
            f"git clone {authenticated_url}",
            shell=True,
            cwd=temporary_folder.name,
            stdout=subprocess.DEVNULL,
        )
        os.chdir(branch_path)
        target_repo = get_all_files(branch_path)
        target_repo = [f[len(f"{branch_path}/") :] for f in target_repo]

        # Name the new branch
        branch_name = f'{BOT_NAME}-{datetime.datetime.now().strftime("%Y%m%d")}-{random_string(length=8)}'
        created_branch = False

        # get the list of files to ignore
        IGNORE = DEFAULT_BOTIGNORE
        ignore_file = branch_path / ".botignore"
        if ignore_file.exists():
            with ignore_file.open(mode="r") as f:
                IGNORE = DEFAULT_BOTIGNORE + f.read().splitlines()

        for path in source_repo:

            message = f"path: {path} "

            if path.replace("\\", "/") in IGNORE:
                self.logger.debug(message + "ignoring")
                continue

            if (template_path / path).is_file():

                if not (branch_path / path).exists():
                    self.logger.debug(message + "is new")
                    if not created_branch:
                        subprocess.run(
                            f"git checkout -b {branch_name}",
                            shell=True,
                            cwd=branch_path,
                            stdout=subprocess.DEVNULL,
                        )
                        created_branch = True
                    os.makedirs((branch_path / path).parent, exist_ok=True)
                    shutil.copy2(template_path / path, branch_path / path)
                    subprocess.run(
                        f'git add "{path}"',
                        shell=True,
                        cwd=branch_path,
                        stdout=subprocess.DEVNULL,
                    )
                else:
                    with open(template_path / path, "rb") as f:
                        source_file_contents = f.read()
                    with open(branch_path / path, "rb") as f:
                        target_file_contents = f.read()
                    if source_file_contents != target_file_contents:
                        self.logger.debug(message + "needs to be updated")
                        if not created_branch:
                            subprocess.run(
                                f"git checkout -b {branch_name}",
                                shell=True,
                                cwd=branch_path,
                                stdout=subprocess.DEVNULL,
                            )
                            created_branch = True
                        os.makedirs((branch_path / path).parent, exist_ok=True)
                        shutil.copy2(template_path / path, branch_path / path)
                        subprocess.run(
                            f'git add "{path}"',
                            shell=True,
                            cwd=branch_path,
                            stdout=subprocess.DEVNULL,
                        )
                    else:
                        self.logger.debug(message + "needs no action")

        if created_branch:

            subprocess.run(
                f'git config --global user.email "xb500@users.noreply.github.com"',
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                f"git config --global user.name {BOT_NAME}",
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                f"git remote set-url origin {authenticated_url}",
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                f"git remote set-url --push origin {authenticated_url}",
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                f"git remote set-url --pull origin {authenticated_url}",
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                'git commit -m "sync with template"',
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                f"git push {authenticated_url} {branch_name}",
                shell=True,
                cwd=branch_path,
                stdout=subprocess.DEVNULL,
            )

            GitHubAdapter.submit_pr(  # type:ignore
                owner=self.ORGANIZATION,
                repository_name=THIS_REPO,
                branch_name=branch_name,
                target_branch="main",
                authentication_token=self.AUTH_TOKEN,  # type:ignore
                title=f"sync with template",
                comments=self.comments,
            )

        os.chdir("../..")
        temporary_folder.cleanup()

        return data, context
