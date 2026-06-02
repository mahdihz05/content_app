import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)


def wait_for_element(
    driver,
    by,
    value,
    timeout=20
):

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_clickable(
    driver,
    by,
    value,
    timeout=20
):

    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


def safe_click(
    driver,
    by,
    value,
    timeout=20,
    retries=3
):

    last_error = None

    for _ in range(retries):

        try:

            element = wait_clickable(
                driver,
                by,
                value,
                timeout
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )

            time.sleep(0.5)

            element.click()

            return element

        except (
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ) as e:

            last_error = e

            time.sleep(1)

    raise last_error


def safe_send_keys(
    driver,
    by,
    value,
    text,
    timeout=20,
    clear=True
):

    element = wait_for_element(
        driver,
        by,
        value,
        timeout
    )

    if clear:

        element.clear()

    element.send_keys(text)

    return element