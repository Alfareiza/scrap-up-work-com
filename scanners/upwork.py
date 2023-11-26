import re
from typing import Tuple, List, Dict, Any

from bs4 import BeautifulSoup, Tag
from selenium.common import TimeoutException

from resources.base import BaseSelenium, UpWorkProfile, Scanner
from resources.error_messages import (
    ERRORS,
    RESET_SECURITY_QUESTION,
    TECHNICAL_DIFFICULTIES,
    USERNAME_INCORRECT
)
from resources.exceptions import CloudFareException, LoginFailed
from resources.models import ProfileSchema, JobSchema
from settings import BASE_DIR, logger as log


class UpWorkScanner(BaseSelenium, Scanner):
    URL = 'https://www.upwork.com/'

    def __init__(self, info: dict | UpWorkProfile) -> None:
        BaseSelenium.__init__(self, preload_driver=False)
        Scanner.__init__(self)

        if not isinstance(info, (dict, UpWorkProfile)):
            raise Exception('info must be a dict or Profile.')
        else:
            if isinstance(info, dict):
                self.profile = UpWorkProfile(info=info)
            elif isinstance(info, UpWorkProfile):
                self.profile = info

        self.login_url = f'{self.URL}ab/account-security/login'
        self.login_attempts = 0
        self.scanned_data: Dict[str, Any] = {}

    def login(self) -> bool:
        """
        Login into self.login_url with credentials of profile.
        """
        self.login_attempts += 1
        log.info('Starting login process')
        self.custom_request(self.login_url, 'id', 'login_username')

        if self.driver.title == 'Just a moment...':
            raise CloudFareException

        try:
            self.step_username()
            self.step_password()
            self.step_secret_answer()
        except Exception as e:
            log.error(f'Error attempting to log in: {e}')
            self.driver.close()
            return False
        else:
            if error_message := self.detect_html_message_errors():
                self.strategy(error_message)
                return self.login()
            else:
                if 'Login' not in self.driver.title:
                    log.info('Logged in successfully')
                    return True
                else:
                    return False

    # @logtime('')
    def step_username(self) -> None:
        """Put the name of the user into the respective field
        and click in a button for confirmation."""
        log.info('Typing username...')
        self.put_text(self.profile.username, 'id', 'login_username')
        self.click_on('xpath', '//button[text()="Continue with Email"]')
        self.time_wait()
        log.info('Username typed')

    # @logtime('')
    def step_password(self) -> None:
        """Put the password of the user into the respective field
        and click in a button for confirmation."""
        log.info('Typing password...')
        self.put_text(self.profile.password, 'xpath', '//input[@name="login[password]"]')
        self.click_on('xpath', '//button[text()="Log in"]')
        log.info('Password typed')
        self.time_wait(6, 10)

    # @logtime('')
    def step_secret_answer(self) -> None:
        """Put the secret answer of the user into the respective field
        and click in a button for confirmation in case this step is
        necessary into the login process."""
        log.info('Checking if is necessary to complete the secret answer step')
        try:
            bool(self.get_element('xpath', '//button[text()="Continue"]'))
        except TimeoutException:
            log.info('Secret-answer step did not appeared in the login process')
        else:
            log.info('Typing secret-answer...')
            self.put_text(self.profile.secret_answer, 'id', 'login_answer')
            self.click_on('xpath', '//button[text()="Continue"]')
            self.time_wait(7, 10)
            log.info('Secret-answer typed...')

    def detect_html_message_errors(self) -> str:
        """
        Detect if in the current state of the site, there is at least one
        of the errors in the constant ERRORS.
        :return: Text of the error.
        """
        result = list(filter(lambda txt: txt in self.driver.page_source, ERRORS))
        if result:
            return result[0]
        return ''

    def strategy(self, strategy_name) -> None:
        """
        Initially executed in case there is an errror in the login process, so
        execute a certain strategy.
        Here can be defined actions to do in case of specific situations.
        :param strategy_name: Name of the stratefy to be executed.
        """
        strategy = {
            USERNAME_INCORRECT: self.change_username,
            TECHNICAL_DIFFICULTIES: self.in_case_of_undetected_error,
            RESET_SECURITY_QUESTION: self.change_username,
        }
        if func := strategy.get(strategy_name):
            func()

    def change_username(self) -> None:
        """Strategy to be executed in order to change the username."""
        match self.login_attempts:
            case 1:
                log.info(f'After {self.login_attempts} attempts, changing the username')
                self.profile.username = self.profile.info.get('username_backup_one')
            case 2:
                log.info(f'After {self.login_attempts} attempts, changing the username')
                self.profile.username = self.profile.info.get('username_backup_two')
            case _:
                raise LoginFailed('3 Attempts of login were tried, and it '
                                  'wasn\t possible to login due to the username '
                                  'which is incorrect.')

    def in_case_of_undetected_error(self) -> None:
        """Strategies to do in case of the error message
        "technical difficulties" appeared in the html."""
        ...

    def parse_job(self, job: Tag) -> dict:
        """
        Scrap the job element in order to get all the information possible.
        Then it is normalized and return it as a dict.
        :param job: Object with information of a job.
        :return: Information of the job in a dictionary.
        """
        job_as_dct = {}
        upper_div, lower_div = job.find_all('div', recursive=False)

        # if element_h2 := upper_div.find('h2'):
        if element_h2 := upper_div.find(class_='job-tile-title'):
            job_as_dct['title'] = element_h2.text.strip()

        # '/jobs/Extract-existing-code-analyse-backgammon-position_~01bb2d063f7fd7f007/?referrer_url_path=find_work_home'
        if element_a := upper_div.find('a'):
            job_as_dct['link'] = element_a.get('href')

        # 'Hourly: $10-$25'
        job_as_dct['job_type'] = self.get_text_element_by_attr(lower_div,
                                                               'data-test',
                                                               'job-type')

        # '23 hours ago'
        job_as_dct['posted_on'] = self.get_text_element_by_attr(lower_div,
                                                                'data-test',
                                                                'posted-on')

        # Less than 30 hrs/week
        job_as_dct['workload'] = self.get_text_element_by_attr(lower_div,
                                                               'data-test',
                                                               'workload')

        # '$ 150 '
        job_as_dct['budget'] = self.get_text_element_by_attr(lower_div,
                                                             'data-test',
                                                             'budget')

        # 'Less than 1 month'
        job_as_dct['duration'] = self.get_text_element_by_attr(lower_div,
                                                               'data-test',
                                                               'duration')

        # 'Intermediate'
        job_as_dct['contractor_tier'] = self.get_text_element_by_attr(lower_div,
                                                                      'data-test',
                                                                      'contractor-tier')

        # 'Experience Level'
        job_as_dct['tier_label'] = self.get_text_element_by_attr(lower_div,
                                                                 'data-test',
                                                                 'tier-label')

        # 'Python explanation with exercises how to work it out'
        job_as_dct['description'] = self.get_text_element_by_attr(lower_div,
                                                                  'data-test',
                                                                  'job-description-text')

        # {'Data Interpretation', 'Python', 'Data Analysis'}
        if matches := lower_div.find_all(attrs={"data-test": "attr-item"}):
            job_as_dct['skills'] = [match.get_text(strip=True) for match in matches]

        # 'Payment unverified'
        job_as_dct['verification_status'] = self.get_text_element_by_attr(lower_div,
                                                                          'data-test',
                                                                          'verification-status')

        # 'Rating is 0 out of 5.'
        if match := lower_div.find(attrs={'data-test': 'js-feedback'}):
            if rating := match.find('span', class_='sr-only'):
                job_as_dct['rating'] = rating.get_text(strip=True)

        # '$4K+'
        job_as_dct['spendings'] = self.get_text_element_by_attr(lower_div, 'data-test',
                                                                'client-spendings')

        # 'Ireland'
        job_as_dct['country'] = self.get_text_element_by_attr(lower_div, 'data-test',
                                                              'client-country')

        return self.normalize_job(job_as_dct)

    def normalize_job(self, job: dict) -> dict:
        """
        Create dictionary in order to present the final normalized job
        to the rest of the project.
        Here, is possible to cast some data, clean it, validate it, or prepare it
        to send it to the db and/or be exported.
        :param job: Dictionary with the information recenlty captured.
        :return: Dictionary with all the captured information of the job.
        """
        return {
            'title': job.get('title', ''),
            'link': self.get_absolute_url(job.get('link', '')),
            'job_type': job.get('job_type', ''),
            'posted_on': job.get('posted_on', ''),
            'workload': job.get('workload', ''),
            'budget': job.get('budget', ''),
            'duration': job.get('duration', ''),
            'contractor_tier': job.get('contractor_tier', ''),
            'tier_label': job.get('tier_label', ''),
            'description': job.get('description', ''),
            'verification_status': job.get('verification_status', ''),
            'skills': job.get('skills', {}),
            'rating': job.get('rating', ''),
            'spendings': job.get('spendings', ''),
            'country': job.get('country', ''),
        }

    def get_absolute_url(self, link: str) -> str:
        """
        Compute the absolute url of a link.
        :param link: Representation of an url
                Ex.: '/jobs/.../?referrer_url_path=find_work_home'
        :return: Absolute form of URL
        Ex.: 'https://www.upwork.com/jobs/.../?referrer_url_path=find_work_home'
        """
        if link:
            if link.startswith('/'):
                link = self.URL + link[1:]
        return link

    @staticmethod
    def catch_jobs(content: BeautifulSoup) -> List[Tag]:
        """
        Discover the jobs considering that they are into the next div:
            <div data-test="job-tile-list"> ...jobs... </div>
        :param content: Instance of BeautifulSoup which depicts the content of a site.
        :return: Result of having search jobs.
        """
        jobs: List[Tag] = []
        div_base = content.find('div', {"data-test": "job-tile-list"})
        if div_base and isinstance(div_base, Tag):
            jobs = div_base.find_all('section', recursive=False)
        return jobs

    @staticmethod
    def prepare_data(html_content: str, name_page: str) -> BeautifulSoup:
        """
        Given a html content of a page, a file is created with that information
        :param name_page:
        :param html_content: String which depicts the content of a site.
        :return: BeautifulSoup instance with the html data.
        """
        filepath = BASE_DIR / 'files' / f'upwork_{name_page}.html'
        log.info(f'Creating file {filepath.name}')
        filepath.write_text(html_content)

        with open(filepath) as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup

        # with TemporaryFile() as fp:
        #     fp.write(html_content.encode())
        #     fp.seek(0)
        #     soup = BeautifulSoup(fp.read(), 'html.parser')
        # return soup

    @staticmethod
    def find_profile_url(html_content: str) -> str:
        """
        Look up the url of the profile using regular expression.
        :param html_content: String which depicts the content of a site.
        :return: Url of the profile:
                Ex.: 'https://upwork.com/freelancers/~011cfba3bd0cf44f8d'
        """
        log.info('Discovering profile url in current state of site')
        match = re.search(r'profileUrl:"([^"]+)"', html_content)
        if match:
            log.info('Profile URL found successfully')
            return match.group(1).encode('utf-8').decode('unicode-escape')
        log.info('Profile URL wasn\'t found')
        return ''

    @staticmethod
    def get_info_identity(profile_soup: BeautifulSoup) -> Tuple[str, str, str, str, str]:
        """
        Scan the information about the identity of the user.
        :param profile_soup: Element with the information of a specific part
                            of the site.
        :return: Tuple with 5 elements, either empty or not. They are:
                name, picture_url, locality, country and local_time
        """

        name, picture_url, locality, country, local_time = '', '', '', '', ''
        info_user = profile_soup.find('div', class_='identity-container')
        if info_user and isinstance(info_user, Tag):

            name_found = info_user.find(attrs={'itemprop': 'name'})
            if isinstance(name_found, Tag):
                name = name_found.get_text(strip=True)

            picture_url_found = profile_soup.find('img')
            if isinstance(picture_url_found, Tag):
                picture_url_found_content = picture_url_found.get('src')
                if picture_url_found_content and isinstance(picture_url_found_content, str):
                    picture_url = picture_url_found_content

            locality_found = info_user.find(attrs={'itemprop': 'locality'})
            if isinstance(locality_found, Tag):
                locality = locality_found.get_text(strip=True)

            country_found = info_user.find(attrs={'itemprop': 'country-name'})
            if isinstance(country_found, Tag):
                country = country_found.get_text(strip=True)

            local_time_found = info_user.find('div', class_='time')
            if isinstance(local_time_found, Tag):
                local_time = local_time_found.get_text(strip=True)
                local_time = local_time.replace('–', '').replace(" local time", "")

        else:
            log.warning('The div with class identity-container was not found')

        return name, picture_url, locality, country, local_time

    @staticmethod
    def get_info_profile(section: Tag) -> Tuple[str, str, str]:
        """
        Scan the information about the profile of the user.
        :param section: Element with the information of a specific part
                        of the site.
        :return: Tuple with 3 elements, either empty or not. role, value_hr and desc
        """
        # 5 sections: main_info, work_history, portfolio, skills, catalog.
        sections = section.find_all('section', recursive=False)
        len_sections = len(sections)

        role, value_hr, desc = '', '', ''

        # Capturing main_info
        if len_sections:
            if role := sections[0].find('h2'):
                role = role.get_text(strip=True)

            if value_hr := sections[0].find(attrs={'role': 'presentation'}):
                value_hr = value_hr.get_text(strip=True)

            if desc := sections[0].find('span', attrs={'role': 'text-body'}):
                desc = desc.get_text(strip=True)

        # Scanning work_history
        # if len_sections >= 2:
        #     ...

        # Scanning portfolio
        # if len_sections >= 3:
        #     ...

        # Scanning skills
        # if len_sections >= 4:
        #     ...

        # Scanning catalog
        # if len_sections >= 5:
        #     ...

        return role, value_hr, desc

    @staticmethod
    def get_info_employment(section: Tag) -> List:
        """
        Scan the information about the employment history.
        :param section: Element with the information of a specific part
                        of the site.
        :return: Information of the employments.
             Ex.: [
                    {'role': 'Software Developer', 'employer': 'Facebook',
                    'initial_period': 'January 2023', 'end_period': 'Present'},
                    {'role': 'Tech Lead', 'employer': 'Twitter',
                    'initial_period': 'January 2021', 'end_period':
                    'January 2023'}
                ]
        """
        employments = section.find_all('h4')
        result = []
        for employment in employments:
            role, employer = employment.get_text(strip=True).split('|')
            info_employment = {'role': role.strip(), 'employer': employer.strip()}

            if period := employment.parent.parent.parent.contents:
                initial_period, end_period = period[2].get_text(strip=True).split('-')
                info_employment['initial_period'] = initial_period.strip()
                info_employment['end_period'] = end_period.strip()

            result.append(info_employment)

        return result

    def parse_profile(self, profile_soup: BeautifulSoup) -> dict:
        """
        Scrap the profile element in order to get all the information possible.
        Then it is normalized and return it as a dict.
        :param profile_soup: Object with information of a profile.
        :return: Information of the profile in a dictionary.
        """
        profile_as_dct = {}
        profile_box = profile_soup.select_one('div[data-qa-profile-viewer-uid]')

        if profile_box and isinstance(profile_box, Tag):

            # 7 Sections: Identity, Profile, Mix, Testimonials,
            # Certifications, Employment History, Experiences
            sections_user = profile_box.find_all(
                'div', class_='profile-outer-card',
                recursive=False)

            log.info(f'Detected {len(sections_user)} sections')

            # '1640798106421293056'
            profile_as_dct['id_account'] = profile_box.get('data-qa-profile-viewer-uid')

            (profile_as_dct['name'], profile_as_dct['picture_url'],
             profile_as_dct['locality'], profile_as_dct['country'],
             profile_as_dct['local_time']) = self.get_info_identity(sections_user[0])

            (profile_as_dct['role'],
             profile_as_dct['value_hr'],
             profile_as_dct['desc']) = self.get_info_profile(sections_user[1])

            profile_as_dct['employment'] = self.get_info_employment(sections_user[5])
        else:
            log.warning('div with information of the profile wasn\'t found')

        return self.normalize_profile(profile_as_dct)

    def normalize_profile(self, profile: dict) -> dict:
        self.profile.parse_job_history(profile.get('employment', []))
        return {
            "account": profile['id_account'],
            "address": {
                "city": profile.get('locality'),
                "line1": "",
                "line2": "",
                # "state": self.get_state_code(profile.get('locality')),
                # "country": self.get_country_code(profile.get('country')),
                "postal_code": ""
            },
            "first_name": "",
            "last_name": "",
            "full_name": profile.get('name'),
            "birth_date": "",
            "email": "",
            "phone_number": "",
            "picture_url": profile.get('picture_url'),
            "employment_status": self.profile.info.get('employment_status', ''),
            "employment_type": "",
            "job_title": profile.get('role'),
            "ssn": "",
            "marital_status": "",
            "gender": "",
            "hire_date": self.profile.info.get('employment_hire_date'),
            "termination_date": self.profile.info.get('employment_termination_date'),
            "termination_reason": None,
            "employer": self.profile.info.get('employer'),
            "base_pay": {
                "amount": "",
                "period": "",
                "currency": ""
            },
            "pay_cycle": "",
            "platform_ids": {
                "employee_id": "",
                "position_id": "",
                "platform_user_id": ""
            },
            "metadata": {}
        }

    def scan_jobs(self, html_content):
        """Scann all the jobs in the main page."""
        log.info('Starting to scan the jobs')
        soup = self.prepare_data(html_content, 'jobs_page')
        jobs = self.catch_jobs(soup)

        log.info(f"Captched {len(jobs)} jobs")

        self.scanned_data['jobs'] = [JobSchema(**self.parse_job(job)) for job in jobs]
        log.info('Scanned of jobs finished')

    def scan_profile(self, profile_url):
        """Scan the profile of the user logged in the upwork account."""
        log.info('Starting to scan the profile')
        self.custom_request(profile_url, 'class name', 'profile-outer-card')
        self.driver.set_window_size(1000, 1080)
        profile_soup = self.prepare_data(self.driver.page_source, 'profile_page')

        self.scanned_data['profile'] = ProfileSchema(**self.parse_profile(profile_soup))
        log.info('Scanned of profile finished')

    def run(self):
        """
        Main function of the class.
            1. Login into the account.
            2. Scan the jobs.
            3. Access into the profile page.
            4. Scan the profile information.
        """
        self.load_driver()
        if self.login():
            self.fullscroll_to_bottom()

            html_content = self.driver.page_source
            self.scan_jobs(html_content)

            if profile_url := self.find_profile_url(html_content):
                self.scan_profile(profile_url)
        self.driver.quit()
