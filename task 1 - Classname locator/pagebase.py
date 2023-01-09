"""
Base class for automating web pages using Selenium WebDriver
This is the base class that all the classes representing various pages
of application inherit from. This class contains all selenium actions.
"""

from enum import Enum
from time import sleep
from retry import retry
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from random import uniform

import json


class PageBase(object):
    """
    Base Class for web related operations using Selenium WebDriver
    """

    def __init__(self, driver,url):
        """
        Provides webdriver instance to the classes inheriting it
        :param browser_type: browser, e.g. IE, Firefox, Chrome
        :param driver: WebDriver object
        """
        self._driver = driver
        if url:
            self.open(url)


    def get_current_title(self):
        return self._driver.title

    def open(self, url):
        """
        Visit the page base_url + url
        :param url: URL to be opened
        :param wait_time: time to wait till url opens
        :return:
        """
        # url = self.base_url + url
        if self._driver.current_url != url:
            self._driver.get(url)

    @retry(StaleElementReferenceException, tries=5, delay=2)  # click using selenium
    def click(self, locator):
        """
        Clicks the given element
        :param locator: Element locator strategy
        :return: element
        """

        element = None
        if isinstance(locator, str):
            element = self.find_element(locator)
        elif isinstance(locator, WebElement):
            element = locator

        if element is not None:
            element.click()
        else:
            raise Exception("Could not click on the element with locator {}".
                            format(locator))

    def get_text(self, locator):
        """
        get  the inner text of given element
        :param locator: Element locator strategy
        :return: text
        """
        if isinstance(locator, WebElement):
            return locator.text
        try:
            element = self.find_element(locator)
        except Exception as e:
            raise TimeoutException("Could not get the text of the the element with locator {} due to {}".
                                   format(locator, e))
        return element.text

    def find_element(self, locator, timeout=1):
        """
        Find and return element based on the given locator value
        E.g: draggableElement = ("xpath@@//div[@id='draggable']")
        :param locator: Element locator strategy
        :return: Element
        """
        try:
            return WebDriverWait(self._driver, timeout=timeout) \
                .until(EC.presence_of_element_located(self.__get_by(locator_with_strategy=locator)),
                       message="Timed out after {} seconds while waiting to find the element with locator {} ".format(
                           timeout, locator))
        except Exception as e:
            raise Exception("Could Not Find Element with locator {} due to error {} ".format(locator, str(e)))

    def __get_by(self, locator_with_strategy):  # to locate element by id/xpath etc
        """
        Get and return By instance based on the locator strategy
        :param locator_with_strategy: Element locator strategy
        :return: By instance of the element
        """

        if "@@" not in locator_with_strategy:
            locator_with_strategy = Strategy.ID.value + "@@" + locator_with_strategy

        strategy_and_locator = str(locator_with_strategy).split("@@")
        strategy = strategy_and_locator[0]
        locator = strategy_and_locator[1]
        by = None
        if strategy == Strategy.XPATH.value:
            by = (By.XPATH, locator)
        elif strategy == Strategy.ID.value:
            by = (By.ID, locator)
        elif strategy == Strategy.CSS.value:
            by = (By.CSS_SELECTOR, locator)
        elif strategy == Strategy.TAGNAME.value:
            by = (By.TAG_NAME, locator)
        else:
            raise Exception(
                " Incorrect locator specified . Locator has to be either xpath,id,css,tagname -->" + locator_with_strategy)
        return by

    def find_elements(self, locator):
        """
        Find and return the list of webelements based on the given locator value
        :param locator: Element locator strategy
        :return: list of the elements
        """
        try:
            return self._driver.find_elements(*self.__get_by(locator_with_strategy=locator))
        except Exception as e:
            raise Exception("Could Not Find Elements with locator {} due to error {}".format(locator, str(e)))

    def sleep_in_seconds(self, seconds=1):
        """
        Method for hard wait as per given seconds
        :param seconds: time in seconds
        :return:
        """
        # justin: add some randomness to do not get detected
        minSec = seconds - 1
        if minSec <= 0:
            minSec = 1
        maxSec = seconds + 1
        sleep(uniform(minSec, maxSec))

    def send_keys(self, locator, *keys):
        """
        send keys to locator
        :param locator: element
        :param wait_time: time to wait
        :return:
        """
        element = self.find_element(locator)
        try:
            element.send_keys(*(keys))
        except Exception as e:
            raise e

    def becomes(self, class_constructor, *args, **kwargs):
        """
        Converts this class to another class given by class_constructor
        :param class_constructor: constructor method of the class
        :return: instance of  class
        """
        return class_constructor(self._driver, *args, **kwargs)

    def javascript_scroll(self, locator):
        element = self.find_element(locator)
        return self._driver.execute_script("arguments[0].scrollIntoView();", element)

    @retry(StaleElementReferenceException, tries=5, delay=2)
    def get_attribute(self, locator, attribute):
        """
        Get the provided attribute value for the given element
        :param locator: Element locator strategy
        :param attribute: attribute
        :return: value of the attribute
        """
        if isinstance(locator, WebElement):
            return locator.get_attribute(attribute)
        else:
            element = self.find_element(locator)
            return element.get_attribute(attribute)

    def wait_till_element_is_present(self, locator, timeout=10):
        """
        WebDriver Explicit wait till element is present
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """

        element = WebDriverWait(self._driver, timeout). \
            until(EC.presence_of_element_located(self.__get_by(locator)),
                  message="Could Not Locate element {} in {} seconds".format(locator, timeout))
        return element

    def is_element_present(self, locator, timeout=1):
        """
        Check the presence of element.
        :return: Boolean
        """
        try:
            WebDriverWait(self._driver, timeout=timeout) \
                .until(EC.presence_of_element_located(self.__get_by(locator)))
        except TimeoutException:
            return False
        except Exception as e:
            raise Exception("Could Not Verify Element Presence {} due to error {}".format(locator, str(e)))
        return True

    def scroll_to_element(self, locator):
        html = self._driver.find_element_by_tag_name('html')
        while not (self.is_element_present(locator)):
            print("Scrolling down to find {}".format(locator))
            html.send_keys(Keys.PAGE_DOWN)
            self.sleep_in_seconds(1)

    def scroll_sequentially(self, straight_to_end=False):
        html = self._driver.find_element_by_tag_name('html')
        # self.sleep_in_seconds(1)
        if straight_to_end:
            html.send_keys(Keys.END)
        else:
            html.send_keys(Keys.PAGE_DOWN)
        self.sleep_in_seconds(2)

    def execute_javascript_click(self, locator):
        element = None
        if isinstance(locator, str):
            element = self.find_element(locator)
        elif isinstance(locator, WebElement):
            element = locator
        self._driver.execute_script("arguments[0].click();", element)

    @retry(StaleElementReferenceException, tries=5, delay=2)
    def find_child_element(self, element, locator, timeout=1):
        """
        find child element of parent element , eg xpath@@.//*[contains(@data-hook,'child-element')]
        """
        by = self.__get_by(locator_with_strategy=locator)
        return WebDriverWait(element, timeout).until(EC.presence_of_element_located(by))

    def find_child_elements(self, element, locator):
        by = self.__get_by(locator_with_strategy=locator)
        return element.find_elements(*by)

    def is_child_element_present(self, element, locator, timeout=1):
        """
        Check the presence of element.
        :return: Boolean
        """
        try:
            self.find_child_element(element, locator, timeout)
        except TimeoutException:
            return False
        except Exception as e:
            raise Exception("Could Not VerifyChild Element Presence {} due to error {}".format(locator, str(e)))
        return True

    def save_cookie(self, path):
        with open(path, 'w') as filehandler:
            json.dump(self._driver.get_cookies(), filehandler)

    def load_cookie(self, path):
        with open(path, 'r') as cookiesfile:
            cookies = json.load(cookiesfile)
        for cookie in cookies:
            self._driver.add_cookie(cookie)


class Strategy(Enum):
    """
    Locator Strategy Constants
    """
    XPATH = "xpath"
    ID = "id"
    CSS = "css"
    TAGNAME = "tag name"