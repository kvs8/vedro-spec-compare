import os
import subprocess
from typing import Tuple

from bs4 import BeautifulSoup


def added_request_file(file_path_with_requests: str) -> None:
    subprocess.run([
        'cp',
        file_path_with_requests,
        os.path.join('launch', os.path.basename(file_path_with_requests))
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
    added_request_file('test_data/coverage/golden.yml')
    added_request_file('test_data/coverage/testing.yml')

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
    assert os.path.exists('launch/coverage.html')

    with open("test_data/coverage/coverage.html", "r") as file1, open("launch/coverage.html", "r") as file2:
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_coverage_report_with_report_path():
    added_request_file('test_data/coverage/golden.yml')
    added_request_file('test_data/coverage/testing.yml')

    stdout, stderr = run(
        command='vsc coverage golden.yml testing.yml --report-path report/coverage.html',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of the test coverage\n"
        "Parsing the golden spec: golden.yml\n"
        "Parsing the testing spec: testing.yml\n"
        "Defining the difference\n"
        "Generating the coverage report: report/coverage.html\n"
    ) == stderr
    assert os.path.exists('launch/report/coverage.html')

    with open("test_data/coverage/coverage.html", "r") as file1, open("launch/report/coverage.html", "r") as file2:
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_coverage_report_with_non_existent_spec_file():
    stdout, stderr = run(
        command='vsc coverage golden.yml testing.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of the test coverage\n"
        "Parsing the golden spec: golden.yml\n"
        "Failed to open file golden.yml: file not found\n"
    ) == stderr


def test_generate_coverage_report_with_fail_fetch_data_by_url():
    incorrect_url = "https://raw.githubusercontent.com/kvs8/vedro-spec-compare/refs/heads/main/golden.yml"
    stdout, stderr = run(
        command=f'vsc coverage {incorrect_url} {incorrect_url}',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of the test coverage\n"
        f"Parsing the golden spec: {incorrect_url}\n"
        f"Failed to fetch data from {incorrect_url}: status is 404\n"
    ) == stderr


def test_generate_discrepancy_report():
    added_request_file('test_data/discrepancy/golden.yml')
    added_request_file('test_data/discrepancy/testing.yml')

    stdout, stderr = run(
        command='vsc discrepancy golden.yml testing.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of discrepancy in doc regarding tests\n"
        "Parsing the golden spec: golden.yml\n"
        "Parsing the testing spec: testing.yml\n"
        "Defining the difference\n"
        "Generating the discrepancy report: discrepancy.html\n"
    ) == stderr
    assert os.path.exists('launch/discrepancy.html')

    with (
        open("test_data/discrepancy/discrepancy.html", "r") as file1,
        open("launch/discrepancy.html", "r") as file2
    ):
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_discrepancy_report_with_report_path():
    added_request_file('test_data/discrepancy/golden.yml')
    added_request_file('test_data/discrepancy/testing.yml')

    stdout, stderr = run(
        command='vsc discrepancy golden.yml testing.yml --report-path report/discrepancy.html',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of discrepancy in doc regarding tests\n"
        "Parsing the golden spec: golden.yml\n"
        "Parsing the testing spec: testing.yml\n"
        "Defining the difference\n"
        "Generating the discrepancy report: report/discrepancy.html\n"
    ) == stderr
    assert os.path.exists('launch/report/discrepancy.html')

    with (
        open("test_data/discrepancy/discrepancy.html", "r") as file1,
        open("launch/report/discrepancy.html", "r") as file2
    ):
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_discrepancy_report_with_non_existent_spec_file():
    stdout, stderr = run(
        command='vsc discrepancy golden.yml testing.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of discrepancy in doc regarding tests\n"
        "Parsing the golden spec: golden.yml\n"
        "Failed to open file golden.yml: file not found\n"
    ) == stderr


def test_generate_discrepancy_report_with_fail_fetch_data_by_url():
    incorrect_url = "https://raw.githubusercontent.com/kvs8/vedro-spec-compare/refs/heads/main/golden.yml"
    stdout, stderr = run(
        command=f'vsc discrepancy {incorrect_url} {incorrect_url}',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination of discrepancy in doc regarding tests\n"
        f"Parsing the golden spec: {incorrect_url}\n"
        f"Failed to fetch data from {incorrect_url}: status is 404\n"
    ) == stderr


def test_generate_changes_report():
    added_request_file('test_data/changes/current.yml')
    added_request_file('test_data/changes/previous.yml')

    stdout, stderr = run(
        command='vsc changes current.yml previous.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination changes to the Open API spec\n"
        "Parsing the current spec: current.yml\n"
        "Parsing the previous spec: previous.yml\n"
        "Defining the difference\n"
        "Generating the changes report: changes.html\n"
    ) == stderr
    assert os.path.exists('launch/changes.html')

    with (
        open("test_data/changes/changes.html", "r") as file1,
        open("launch/changes.html", "r") as file2
    ):
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_changes_report_with_report_path():
    added_request_file('test_data/changes/current.yml')
    added_request_file('test_data/changes/previous.yml')

    stdout, stderr = run(
        command='vsc changes current.yml previous.yml --report-path report/changes.html',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination changes to the Open API spec\n"
        "Parsing the current spec: current.yml\n"
        "Parsing the previous spec: previous.yml\n"
        "Defining the difference\n"
        "Generating the changes report: report/changes.html\n"
    ) == stderr
    assert os.path.exists('launch/report/changes.html')

    with (
        open("test_data/changes/changes.html", "r") as file1,
        open("launch/report/changes.html", "r") as file2
    ):
        soup1 = BeautifulSoup(file1, "html.parser")
        soup2 = BeautifulSoup(file2, "html.parser")

        text1 = soup1.get_text(strip=True)
        text2 = soup2.get_text(strip=True)

        assert text1 == text2
        assert soup1 == soup2


def test_generate_changes_report_with_non_existent_spec_file():
    stdout, stderr = run(
        command='vsc changes current.yml previous.yml',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination changes to the Open API spec\n"
        "Parsing the current spec: current.yml\n"
        "Failed to open file current.yml: file not found\n"
    ) == stderr


def test_generate_changes_report_with_fail_fetch_data_by_url():
    incorrect_url = "https://raw.githubusercontent.com/kvs8/vedro-spec-compare/refs/heads/main/current.yml"
    stdout, stderr = run(
        command=f'vsc changes {incorrect_url} {incorrect_url}',
        cwd=f'{os.getcwd()}/launch'
    )

    assert (
        "Determination changes to the Open API spec\n"
        f"Parsing the current spec: {incorrect_url}\n"
        f"Failed to fetch data from {incorrect_url}: status is 404\n"
    ) == stderr
