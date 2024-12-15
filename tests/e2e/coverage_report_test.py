import os
import subprocess
from typing import Tuple

from bs4 import BeautifulSoup


def added_request_file(file_path_with_requests: str) -> None:
    subprocess.run([
        'cp',
        os.path.join('test_data', os.path.basename(file_path_with_requests)),
        file_path_with_requests
    ], check=True)


def run(command: str, **kwargs) -> Tuple[str, str]:
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs
    )
    stdout, stderr = proc.communicate()
    return stdout.decode(), stderr.decode()


def test_generate_coverage_report():
    added_request_file(os.path.join('launch', 'golden.yml'))
    added_request_file(os.path.join('launch', 'testing.yml'))

    stdout, stderr = run(
        command='vsc coverage golden.yml testing.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of the test coverage\n"
        "Parsing the golden spec: golden.yml\n"
        "Parsing the testing spec: testing.yml\n"
        "Defining the difference\n"
        "Generating the coverage report: coverage.html\n"
    ) == stderr
    assert os.path.exists('test_data/coverage.html')

    with open("test_data/coverage.html", "r") as file1, open("launch/coverage.html", "r") as file2:
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2
