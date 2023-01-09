from selenium import webdriver
from pagebase import PageBase

url = 'http://localhost:8000/abc.html'  # Start a webserver with the html code

driver = webdriver.Chrome()
pg_obj = PageBase(driver, url=url)
pg_obj.sleep_in_seconds(5)
element_list = pg_obj.find_elements(
    locator="xpath@@//*[@class='SlotPicker-day is-active']//input[contains(@id,'slot')]")
for ele in element_list:
    datetime = ele.get_attribute('data-datetime-label')
    id = ele.get_attribute('id')
    value = ele.get_attribute('value')
    print("Time - {} , ID - {} , Value - {}".format(datetime, id, value))
