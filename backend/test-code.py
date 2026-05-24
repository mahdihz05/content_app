from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
import time
import logging

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_element(driver, by, value, timeout=15, description=""):
    """صبر کردن برای ظاهر شدن المنت"""
    try:
        logger.info(f"در حال انتظار برای: {description or value}")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        logger.info(f"✓ المنت پیدا شد: {description or value}")
        return element
    except TimeoutException:
        logger.error(f"✗ المنت پیدا نشد (timeout): {description or value}")
        driver.save_screenshot(f"error_{int(time.time())}.png")
        raise


def click_with_retry(driver, by, value, max_attempts=3, wait_time=2, description=""):
    """کلیک با retry mechanism"""
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"تلاش {attempt}/{max_attempts} برای کلیک: {description}")

            # صبر کنیم تا المنت قابل کلیک باشه
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, value))
            )

            # اسکرول به المنت
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)

            # تلاش برای کلیک معمولی
            element.click()
            logger.info(f"✓ کلیک موفق: {description}")
            return element

        except ElementClickInterceptedException:
            logger.warning(f"⚠ المنت قابل کلیک نیست (overlay روش هست) - تلاش {attempt}")

            # بستن modal/overlay اگر وجود داره
            try:
                close_overlay(driver)
            except:
                pass

            if attempt < max_attempts:
                logger.info(f"صبر {wait_time} ثانیه قبل از تلاش مجدد...")
                time.sleep(wait_time)

                # تلاش با JavaScript click
                try:
                    logger.info("تلاش با JavaScript click...")
                    element = driver.find_element(by, value)
                    driver.execute_script("arguments[0].click();", element)
                    logger.info("✓ کلیک با JavaScript موفق شد")
                    return element
                except Exception as js_error:
                    logger.warning(f"JavaScript click هم کار نکرد: {js_error}")
            else:
                logger.error(f"✗ کلیک ناموفق بعد از {max_attempts} تلاش")
                driver.save_screenshot(f"click_error_{int(time.time())}.png")
                raise

        except Exception as e:
            logger.error(f"✗ خطای غیرمنتظره: {type(e).__name__} - {e}")
            if attempt >= max_attempts:
                driver.save_screenshot(f"error_{int(time.time())}.png")
                raise
            time.sleep(wait_time)

    return None


def click_add_contact_button(driver):
    """
    تلاش برای کلیک روی دکمه اضافه کردن مخاطب با چند روش مختلف
    """
    logger.info("شروع تلاش برای کلیک روی دکمه اضافه کردن...")

    # لیست XPath های مختلف برای دکمه
    button_xpaths = [
        "/html/body/div[4]/div/div/div[2]/div[2]/button",
        "/html/body/div[3]/div/div/div[2]/div[2]/button",
        "//button[contains(text(), 'اضافه')]",
        "//button[contains(text(), 'افزودن')]",
        "//button[contains(text(), 'Add')]",
        "//div[contains(@class, 'modal')]//button[last()]",
        "//div[@role='dialog']//button[last()]"
    ]

    # CSS Selectors هم امتحان می‌کنیم
    button_css_selectors = [
        "button[type='submit']",
        ".modal button:last-child",
        "div[role='dialog'] button:last-child"
    ]

    # تلاش با XPath ها
    for xpath in button_xpaths:
        try:
            logger.info(f"تلاش با XPath: {xpath}")
            element = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ کلیک موفق با XPath: {xpath}")
            return True
        except Exception as e:
            logger.warning(f"⚠ XPath کار نکرد: {xpath}")
            continue

    # تلاش با CSS Selectors
    for css in button_css_selectors:
        try:
            logger.info(f"تلاش با CSS Selector: {css}")
            element = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ کلیک موفق با CSS: {css}")
            return True
        except Exception as e:
            logger.warning(f"⚠ CSS Selector کار نکرد: {css}")
            continue

    # تلاش با JavaScript - پیدا کردن همه دکمه‌ها و کلیک روی آخری
    try:
        logger.info("تلاش با JavaScript برای پیدا کردن دکمه...")
        script = """
        var buttons = document.querySelectorAll('button');
        for (var i = buttons.length - 1; i >= 0; i--) {
            var btn = buttons[i];
            var text = btn.textContent || btn.innerText;
            if (text.includes('اضافه') || text.includes('افزودن') || text.includes('Add')) {
                btn.click();
                return true;
            }
        }
        return false;
        """
        result = driver.execute_script(script)
        if result:
            logger.info("✓ کلیک با JavaScript موفق شد")
            return True
    except Exception as e:
        logger.warning(f"⚠ JavaScript هم کار نکرد: {e}")

    # اگر هیچ کدوم کار نکرد، Enter رو امتحان می‌کنیم
    try:
        logger.info("تلاش با فشردن Enter...")
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        logger.info("✓ Enter فشرده شد")
        return True
    except Exception as e:
        logger.warning(f"⚠ Enter هم کار نکرد: {e}")

    logger.error("✗ هیچ روشی برای کلیک روی دکمه کار نکرد")
    driver.save_screenshot(f"button_not_found_{int(time.time())}.png")
    return False


def close_overlay(driver):
    """بستن modal یا overlay که ممکنه روی صفحه باشه"""
    try:
        logger.info("بررسی وجود overlay/modal...")

        # سعی در پیدا کردن دکمه close
        close_selectors = [
            (By.XPATH, "//button[contains(@class, 'close')]"),
            (By.XPATH, "//div[contains(@class, 'modal')]//button"),
            (By.XPATH, "//div[contains(@class, 'overlay')]//button"),
            (By.XPATH, "//button[@aria-label='Close']"),
            (By.XPATH, "//button[contains(text(), '×')]"),
            (By.CSS_SELECTOR, ".ReactModal__Overlay"),
            (By.CSS_SELECTOR, ".modal-backdrop")
        ]

        for by, selector in close_selectors:
            try:
                close_btn = driver.find_element(by, selector)
                close_btn.click()
                logger.info("✓ overlay/modal بسته شد")
                time.sleep(1)
                return True
            except:
                continue

        logger.info("overlay/modal پیدا نشد")
        return False

    except Exception as e:
        logger.warning(f"خطا در بستن overlay: {e}")
        return False


def send_keys_safe(driver, by, value, text, description=""):
    """ارسال متن با error handling"""
    try:
        logger.info(f"ارسال متن به: {description}")
        element = wait_for_element(driver, by, value, description=description)
        element.clear()
        element.send_keys(text)
        logger.info(f"✓ متن ارسال شد: {description}")
        return element
    except Exception as e:
        logger.error(f"✗ خطا در ارسال متن: {e}")
        driver.save_screenshot(f"send_keys_error_{int(time.time())}.png")
        raise


def main():
    driver = None
    try:
        logger.info("=" * 60)
        logger.info("شروع اتوماسیون بله")
        logger.info("=" * 60)

        # مسیر chromedriver
        service = Service(r"C:\Users\m.hosseinzadeh\Downloads\chromedriver-win64\chromedriver.exe")

        logger.info("راه‌اندازی Chrome driver...")
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        logger.info("✓ Chrome driver آماده است")

        # -----------------------
        # باز کردن سایت بله
        # -----------------------
        logger.info("باز کردن سایت بله...")
        driver.get("https://web.bale.ai")
        time.sleep(5)
        logger.info("✓ سایت بله بارگذاری شد")

        # -----------------------
        # دکمه اول (ENTER)
        # -----------------------
        logger.info("کلیک روی دکمه اول...")
        first_button = wait_for_element(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/button",
            description="دکمه اول"
        )
        first_button.send_keys(Keys.ENTER)
        time.sleep(2)
        logger.info("✓ دکمه اول کلیک شد")

        # -----------------------
        # دکمه دوم (ENTER)
        # -----------------------
        logger.info("کلیک روی دکمه دوم...")
        second_button = wait_for_element(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div/div[3]/div[2]/div/button",
            description="دکمه دوم"
        )
        second_button.send_keys(Keys.ENTER)
        time.sleep(2)
        logger.info("✓ دکمه دوم کلیک شد")

        # -----------------------
        # وارد کردن شماره تلفن
        # -----------------------
        logger.info("وارد کردن شماره تلفن...")
        phone_input = send_keys_safe(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[1]/div/div[4]/div/fieldset/div/input",
            "9921296785",
            description="فیلد شماره تلفن"
        )
        phone_input.send_keys(Keys.ENTER)
        logger.info("✓ شماره تلفن وارد شد")

        # -----------------------
        # وارد کردن کد تایید
        # -----------------------
        time.sleep(3)
        logger.info("منتظر وارد کردن کد تایید...")
        code_input = wait_for_element(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/fieldset/div/input",
            description="فیلد کد تایید"
        )
        logger.info("⚠ لطفاً کد تایید را دستی وارد کنید")
        # code_input.send_keys("12345")

        # -----------------------
        # صبر برای لود کامل
        # -----------------------
        logger.info("صبر برای لود کامل صفحه...")
        time.sleep(10)
        logger.info("✓ صفحه لود شد")

        # -----------------------
        # رفتن به مخاطبین
        # -----------------------
        logger.info("رفتن به بخش مخاطبین...")
        contacts_button = click_with_retry(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[1]/div/div[4]",
            description="دکمه مخاطبین"
        )
        time.sleep(2)
        logger.info("✓ وارد بخش مخاطبین شدیم")

        # -----------------------
        # افزودن مخاطب
        # -----------------------
        logger.info("کلیک روی افزودن مخاطب...")
        add_contact = click_with_retry(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[2]/div/div[1]/div[1]/ul/div[3]",
            description="دکمه افزودن مخاطب"
        )
        time.sleep(2)
        logger.info("✓ پنجره افزودن مخاطب باز شد")

        # -----------------------
        # وارد کردن شماره مخاطب
        # -----------------------
        logger.info("وارد کردن شماره مخاطب...")
        contact_phone = send_keys_safe(
            driver,
            By.XPATH,
            "/html/body/div[3]/div/div/div[2]/div[2]/div[2]/fieldset/div/input",
            "9331476742",
            description="فیلد شماره مخاطب"
        )
        logger.info("✓ شماره مخاطب وارد شد")

        # -----------------------
        # وارد کردن نام مخاطب
        # -----------------------
        logger.info("وارد کردن نام مخاطب...")
        contact_name = send_keys_safe(
            driver,
            By.XPATH,
            "/html/body/div[3]/div/div/div[2]/div[2]/div[3]/fieldset/div/input",
            "myself2",
            description="فیلد نام مخاطب"
        )
        logger.info("✓ نام مخاطب وارد شد")

        # -----------------------
        # کلیک روی دکمه اضافه کردن مخاطب (با روش جدید)
        # -----------------------
        time.sleep(1)  # یه لحظه صبر می‌کنیم
        success = click_add_contact_button(driver)

        if not success:
            logger.error("✗ نتونستیم روی دکمه کلیک کنیم")
            raise Exception("دکمه اضافه کردن پیدا نشد")

        time.sleep(3)
        logger.info("✓ مخاطب اضافه شد")

        # -----------------------
        # سرچ مخاطب
        # -----------------------
        logger.info("کلیک روی دکمه جستجو...")
        search_user_btn = click_with_retry(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div",
            max_attempts=5,
            wait_time=2,
            description="دکمه جستجوی کاربر"
        )
        logger.info("✓ دکمه جستجو کلیک شد")

        logger.info("وارد کردن نام در جستجو...")
        search_box = send_keys_safe(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/input",
            "myself2",
            description="باکس جستجو"
        )
        time.sleep(3)
        logger.info("✓ جستجو انجام شد")

        # -----------------------
        # انتخاب مخاطب
        # -----------------------
        logger.info("انتخاب مخاطب از نتایج...")
        user_result = click_with_retry(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[2]/div[2]/div/div[1]/div/div[2]",
            description="نتیجه جستجوی کاربر"
        )
        time.sleep(2)
        logger.info("✓ مخاطب انتخاب شد")

        # -----------------------
        # ارسال پیام
        # -----------------------
        logger.info("ارسال پیام...")
        message_input = send_keys_safe(
            driver,
            By.XPATH,
            "/html/body/div[1]/div/div/div/div[4]/div[4]/div/div[3]/div/div[1]",
            "سلام این یک تست است",
            description="فیلد پیام"
        )
        message_input.send_keys(Keys.ENTER)
        time.sleep(5)
        logger.info("✓ پیام ارسال شد")

        # -----------------------
        # برگشت به صفحه اصلی
        # -----------------------
        logger.info("برگشت به صفحه اصلی...")
        driver.get("https://web.bale.ai")
        time.sleep(5)
        logger.info("✓ برگشت به صفحه اصلی")

        logger.info("=" * 60)
        logger.info("✓✓✓ اتوماسیون با موفقیت کامل شد ✓✓✓")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗✗✗ خطای کلی در برنامه ✗✗✗")
        logger.error(f"نوع خطا: {type(e).__name__}")
        logger.error(f"پیام خطا: {e}")
        logger.error("=" * 60)

        # اسکرین‌شات نهایی
        if driver:
            try:
                screenshot_path = f"final_error_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"اسکرین‌شات خطا ذخیره شد: {screenshot_path}")
            except:
                pass

    finally:
        # بستن browser
        if driver:
            logger.info("بستن browser...")
            time.sleep(2)
            driver.quit()
            logger.info("✓ browser بسته شد")


if __name__ == "__main__":
    main()
