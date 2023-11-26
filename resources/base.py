import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any, Dict

from bs4 import Tag
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import NewConnectionError, MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager

from settings import logger as log
from utils.date_utils import period_to_date, date_to_str


class BaseSelenium:
    BY = {"id": By.ID, "xpath": By.XPATH, "link text": By.LINK_TEXT,
          "partial link text": By.PARTIAL_LINK_TEXT,
          "name": By.NAME, "tag name": By.TAG_NAME,
          "class name": By.CLASS_NAME, "css selector": By.CSS_SELECTOR}

    def __init__(self, preload_driver=False):
        """
        Initialize the basic settings to access the site.
        with selenium. When is started, opens a window.
          Chrome. If the argument "--headless=new" is added
          will it appear visually, if not, it is opened "from behind"
        """

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('--disable-application-cache')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--headless")
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        self.options.add_argument(f'user-agent={user_agent}')

        if preload_driver:
            self.driver = webdriver.Chrome(options=self.options,
                                           service=webdriver.ChromeService(
                                               ChromeDriverManager().install())
                                           )

    def load_driver(self):
        self.driver = webdriver.Chrome(options=self.options,
                                       service=webdriver.ChromeService(
                                           ChromeDriverManager().install()
                                       )
                                       )

    def custom_request(self, url, type_element, value) -> None:
        """
        Try to reach a site by the 3 times. Otherwise, will raise an exception.
        :param url: Address of the website to be checked/accessed.
        :param type_element: Type of element that will be checked. This parameter
                              will be used in the has_page_loaded function.
        :param value: Value of the type_element that will be checked.
        :return: If the page does not load, raise an exception.
        """
        is_site_loaded = False
        attempts = 0
        while not is_site_loaded and attempts != 4:
            try:
                self.open_url(url)
                attempts += 1
                is_site_loaded = self.has_page_loaded(type_element, value)
            except MaxRetryError as e:
                log.error(f"Error={e}")

        if is_site_loaded:
            log.info(f"Site loaded after {attempts} attempts")
        else:
            raise Exception(f'In {attempts} attempts the site '
                            f'wasn\'t possible to reach -> {url}')

    def has_page_loaded(self, type_element: str, value: str) -> bool:
        """Verify if the site has already loaded through check if an
        element is located.
        :param type_element: Type of element to be located.
        :param value: Value of the element to be located.
        :return: True if the site has loaded, otherwise, False.
        """
        timeout = 60
        try:
            element_present = EC.presence_of_element_located((self.BY[type_element], value))
            WebDriverWait(self.driver, 60).until(element_present)
            return True
        except (TimeoutException,):
            self.driver.save_screenshot(f'site_unreachable_{datetime.now():%D_%T}.png')
            log.error(f"Timeout Exception: site didn't load in {timeout} seconds")
            self.driver.quit()
            return False

    def open_url(self, url):
        """
        Open an url using the web driver. Then, establish a width and height.
        :param url: Url to be reached.
        """
        try:
            log.info(f'Opening {url=}')
            self.driver.get(url)
        except (NewConnectionError, MaxRetryError, ConnectionRefusedError) as e:
            log.error(f'{url=} unreachable, ERROR={e}')
            # log.info('Taking screenshot of the site and saving it')
            # self.driver.save_screenshot(f'site_didnt_loaded_{datetime.now():%g_%h_%H_%M}.png')
        else:
            self.driver.set_window_size(1920, 1080)
            self.time_wait()

    @staticmethod
    def time_wait(start=4, end=10):
        """Sleep the execution for seconds, between start and end.
        This function is convenient to demonstrate a non-bot behavior."""
        time.sleep(random.randint(start, end))

    def exect_js(self, script_content):
        """Execute the script coming in script_content"""
        if 'return' in script_content:
            return self.driver.execute_script(script_content)
        self.driver.execute_script(script_content)

    # @logtime('')
    def get_element(self, type_element: str, value: str):
        """Obtain an element until it appears, otherwise will raise  TimeoutException."""
        # element_present = EC.presence_of_element_located((self.BY[type_element], value))
        element_present = EC.visibility_of_element_located((self.BY[type_element], value))
        return WebDriverWait(self.driver, 30).until(element_present)

    def get_elements(self, type_element: str, value: str):
        """Obtain all the elements of type_element with value."""
        return self.driver.find_elements(self.BY[type_element], value)

    def click_on(self, type_element: str, value: str):
        """Click on a found element, by his type_element and value."""
        element = self.get_element(type_element, value)
        element.click()

    def fullscroll_to_bottom(self) -> None:
        """Make one scroll per time until reach the bottom of the site.
         This guarantee that the site has loaded completely their elements.
         This function is convenient for those site which only load their
         html elements when they are shown."""
        log.info('Scrolling down for loading html elements')
        self.driver.set_window_size(1000, 1080)
        self.time_wait(2, 5)
        vertical_distance = self.exect_js('return document.body.scrollHeight;')
        lance = vertical_distance // 10
        scrolled = 0
        while scrolled <= vertical_distance // 5:
            scrolled += lance
            self.driver.execute_script(f"window.scrollTo(0, {scrolled});")
            self.time_wait(8, 16)

        log.info('Scrolling has finished')

    def put_text(self, info, type_element: str, value: str):
        """Type a text into a found element."""
        element = self.get_element(type_element, value)
        element.send_keys(info)


@dataclass
class UpWorkProfile:
    username: Optional[str] = ''
    password: Optional[str] = ''
    secret_answer: Optional[str] = ''
    info: Dict[str, Optional[str]] = field(default_factory=dict)

    def __post_init__(self):
        if self.info:
            self.username = self.info.get('username')
            self.password = self.info.get('password')
            self.secret_answer = self.info.get('secret_answer')

    def parse_job_history(self, job_history: list[dict[Any, Any]]) -> None:
        """
        Given a list with dictionaries where every dict depicts
        a job of the profile. It parses it and add up the information
        to the info attr.
        :param job_history: Information of the employment history:
                            Ex.: [
                                    {'role': 'Software Developer',
                                    'employer': 'Facebook',
                                    'initial_period': 'January 2023',
                                    'end_period': 'Present'},
                                    {'role': 'Tech Lead', 'employer': 'Twitter',
                                    'initial_period': 'January 2021',
                                    'end_period': 'January 2023'}
                                ]
        """
        self.set_employment_status(job_history)

        self.set_employment_termination_date(job_history)

    def set_employment_status(self, job_history: List) -> None:
        """
        Given an information of the employment history, define if
        is currently working or not.
        Add the keys 'employment_status', 'employer' and 'employment_hire_date'
        to the attr info.
        :param job_history: Information of the employment history:
                            Ex.: [
                                    {'role': 'Software Developer',
                                    'employer': 'Facebook',
                                    'initial_period': 'January 2023',
                                    'end_period': 'Present'},
                                    {'role': 'Tech Lead', 'employer': 'Twitter',
                                    'initial_period': 'January 2021',
                                    'end_period': 'January 2023'}
                                ]
        :return: None
        """
        self.info['employment_status'] = None
        self.info['employer'] = None
        self.info['employment_hire_date'] = None
        if job_history:
            if job := list(filter(lambda job: 'present' in job['end_period'].lower(), job_history)):
                self.info['employment_status'] = 'active'
                self.info['employer'] = job[0]['employer']
                last_job_date = period_to_date(job[0]['initial_period'])
                self.info['employment_hire_date'] = date_to_str(last_job_date)
            else:
                ############################################################
                # Define the logic to determinate when is considered       #
                # a profile as retired or terminated                       #
                ############################################################
                self.info['employment_status'] = 'inactive'

    def set_employment_termination_date(self, job_history: List) -> None:
        """
        Given an information of the employment history, define what's the
        date of termination of his last job.
        Add the key 'employment_termination_date' to the attr info with the
        possible values None or '2020-04-08' (Example).
        :param job_history: Information of the employment history:
                            Ex.: [
                                    {'role': 'Software Developer',
                                    'employer': 'Facebook',
                                    'initial_period': 'January 2020',
                                    'end_period': 'January 2021'},
                                    {'role': 'Tech Lead', 'employer': 'Twitter',
                                    'initial_period': 'January 2021',
                                    'end_period': 'January 2023'}
                                ]
        :return: None
        """
        self.info['employment_termination_date'] = None
        if not self.info.get('employment_status') == 'active' and job_history:
            if last_job := self.calc_last_job(job_history):
                last_job_date = period_to_date(last_job['end_period'])
                self.info['employment_termination_date'] = date_to_str(last_job_date)

    @staticmethod
    def calc_last_job(job_history: List[dict]) -> dict:
        """
        Given an information of the employment history, define
        what's the last job.
        :param job_history: Information of the employment history:
                            [
                                {'role': 'Software Developer',
                                'employer': 'Facebook',
                                'initial_period': 'January 2020',
                                'end_period': 'January 2021'},
                                {'role': 'Tech Lead', 'employer': 'Twitter',
                                'initial_period': 'January 2021',
                                'end_period': 'January 2023'}
                            ]
        :return: Last job in the job history. If the end_period
                doesn't have the format "%B %Y" , it will return
                an empty dict.
                Ex.: {
                        'role': 'Tech Lead', 'employer': 'Twitter',
                        'initial_period': 'January 2021',
                        'end_period': 'January 2023'
                     }
        """
        last_job = {}
        try:
            last_job = min(job_history,
                           key=lambda job: datetime.now() - period_to_date(job['end_period'])
                           )
        except ValueError:
            log.warning('Date unrecognizable in job history')
        finally:
            return last_job


class Scanner(ABC):
    """Main class for Scanners"""

    @abstractmethod
    def run(self):
        ...

    def get_text_element_by_attr(self, element: Tag, name_attr: str, value_attr: str) -> str:
        """
        Access into an element and try to find a specific attribute name with a specific
        value for that attribute.
        :param element: Previous selected element.
                        Ex.: 'data-test'
        :param name_attr: Name of the attribute to be found.
                          Ex.: 'posted-on'
        :param value_attr: Value of the attrribute to be found with the name_attr
        :return: String content of the eelment found
        """
        if match := element.find(attrs={name_attr: value_attr}):
            return match.get_text(strip=True)
        return ''
