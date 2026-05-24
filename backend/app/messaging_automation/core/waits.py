from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def wait_for_element(driver, by, value, timeout=20):

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )



def wait_for_clickable(driver, by, value, timeout=20):

    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )