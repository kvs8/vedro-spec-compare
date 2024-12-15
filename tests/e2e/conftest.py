import os
import subprocess

import pytest


@pytest.fixture(autouse=True)
def clean_dir(dir_launch: str = "launch") -> None:
    if os.path.exists(dir_launch):
        subprocess.run(['rm', '-r', dir_launch], check=True)
    os.mkdir(dir_launch)
