import pytest
from bs4 import BeautifulSoup

from resources.base import UpWorkProfile
from scanners.upwork import UpWorkScanner
from settings import BASE_DIR


@pytest.fixture
def fake_profile():
    return UpWorkProfile(info={
        'username': 'recruitment+scanners+task@argyle.com',
        'username_backup_one': 'recruitment+scanners+data@argyle.com',
        'username_backup_two': 'recruitment+tasks@argyle.com',
        'password': 'ArgyleAwesome!@',
        'secret_answer': 'Jimmy'
    })


@pytest.fixture()
def upwork_scanner(fake_profile):
    return UpWorkScanner(fake_profile)


@pytest.fixture()
def job_history_active_profile():
    return [
        {'role': 'Software Developer',
         'employer': 'Facebook',
         'initial_period': 'January 2023',
         'end_period': 'Present'},
        {'role': 'Tech Lead', 'employer': 'Twitter',
         'initial_period': 'January 2021',
         'end_period': 'January 2023'}
    ]


@pytest.fixture()
def job_history_inactive_profile():
    return [
        {'role': 'Software Developer',
         'employer': 'Facebook',
         'initial_period': 'January 2023',
         'end_period': 'June 2023'},
        {'role': 'Tech Lead', 'employer': 'Twitter',
         'initial_period': 'January 2021',
         'end_period': 'January 2023'}
    ]


@pytest.fixture()
def jobs_page():
    filepath = BASE_DIR / 'tests' / 'files' / 'upwork_jobs_page_for_testing.html'
    with open(filepath) as file:
        soup = BeautifulSoup(file, 'html.parser')
    return soup


@pytest.fixture()
def jobs(upwork_scanner, jobs_page):
    return upwork_scanner.catch_jobs(jobs_page)


@pytest.fixture()
def profile_page():
    filepath = BASE_DIR / 'tests' / 'files' / 'upwork_profile_page_for_testing.html'
    with open(filepath) as file:
        soup = BeautifulSoup(file, 'html.parser')
    return soup


@pytest.fixture()
def profile_content(upwork_scanner, profile_page):
    return upwork_scanner.parse_profile(profile_page)
