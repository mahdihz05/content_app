import time

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException
)

from messaging_automation.core.waits import (
    wait_for_element,
    wait_for_clickable
)



def safe_click(
        driver,
        by,
        value,
        logger,
        description="",
        retries=3
):

    for attempt in range(1, retries + 1):

        try:

            logger.info(
                f"CLICK -> {description} | attempt={attempt}"
            )

            element = wait_for_clickable(
                driver,
                by,
                value
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )

            time.sleep(1)

            element.click()

            logger.info(f"SUCCESS CLICK -> {description}")

            return element

        except ElementClickInterceptedException:

            logger.warning(
                f"INTERCEPTED CLICK -> {description}"
            )

            try:
                driver.execute_script(
                    "arguments[0].click();",
                    element
                )

                logger.info(
                    f"JS CLICK SUCCESS -> {description}"
                )

                return element

            except Exception as e:
                logger.error(str(e))

        except TimeoutException:

            logger.error(
                f"TIMEOUT CLICK -> {description}"
            )

        except Exception as e:

            logger.error(
                f"ERROR CLICK -> {description} | {e}"
            )

        time.sleep(2)

    raise Exception(f"failed click -> {description}")

def safe_send_keys(
        driver,
        by,
        value,
        text,
        logger,
        description=""
):

    try:

        logger.info(f"SEND_KEYS -> {description}")

        element = wait_for_element(
            driver,
            by,
            value
        )

        element.clear()

        time.sleep(0.5)

        element.send_keys(text)

        logger.info(f"SUCCESS SEND_KEYS -> {description}")

        return element

    except Exception as e:

        logger.error(
            f"ERROR SEND_KEYS -> {description} | {e}"
        )

        raise