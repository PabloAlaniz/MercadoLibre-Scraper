"""HTTP client adapter using Playwright (real browser) to bypass anti-bot detection."""

from dataclasses import dataclass

from log_config import get_logger

logger = get_logger(__name__)

VERIFICATION_TIMEOUT_SECONDS = 120

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class SimpleResponse:
    """Minimal response object compatible with what MercadoLibreScraper.get_page_content expects."""
    text: str
    url: str
    status_code: int

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} for {self.url}")


class PlaywrightHttpClient:
    """HTTP client using Playwright (real Chromium browser) to bypass anti-bot measures.

    Drop-in replacement for requests.Session — only implements .get() and .headers,
    which is all MercadoLibreScraper uses.
    """

    def __init__(self, on_verification_status=None):
        self._playwright = None
        self._browser = None
        self._context = None
        self.headers = {}
        self._on_verification_status = on_verification_status

    def _ensure_browser(self):
        if self._browser is None:
            self._launch_browser(headless=True)

    def _launch_browser(self, headless=True):
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._context = self._browser.new_context(
            user_agent=_USER_AGENT,
            locale="es-AR",
        )
        logger.info("Playwright Chromium browser launched (headless=%s)", headless)

    def _close_browser(self):
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._context = None
        self._browser = None
        self._playwright = None

    @staticmethod
    def _is_verification_redirect(url):
        return "account-verification" in url

    def _notify(self, status, message):
        if self._on_verification_status:
            self._on_verification_status(status, message)

    def _handle_verification(self, verification_url, original_url):
        """Switch to headed mode so the user can complete ML verification manually."""
        logger.info("Verification detected. Switching to headed mode. URL: %s", verification_url)
        self._notify("required", "Verificación requerida. Complete la verificación en la ventana del navegador.")

        self._close_browser()
        self._launch_browser(headless=False)

        page = self._context.new_page()
        page.goto(verification_url, wait_until="commit", timeout=30000)

        try:
            page.wait_for_url(
                lambda url: "account-verification" not in url,
                timeout=VERIFICATION_TIMEOUT_SECONDS * 1000,
            )
        except Exception:
            page.close()
            self._close_browser()
            self._notify("timeout", "Tiempo de verificación agotado. Intente nuevamente.")
            logger.error("Verification timed out after %d seconds", VERIFICATION_TIMEOUT_SECONDS)
            raise Exception(
                f"Verificación no completada en {VERIFICATION_TIMEOUT_SECONDS} segundos."
            )

        self._notify("completed", "Verificación completada. Continuando scraping...")
        logger.info("Verification completed. Extracting cookies and switching back to headless.")

        cookies = self._context.cookies()
        page.close()

        self._close_browser()
        self._launch_browser(headless=True)
        self._context.add_cookies(cookies)

        page = self._context.new_page()
        try:
            response = page.goto(original_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            status = response.status if response else 0
            final_url = page.url
            html = page.content()
            logger.info("Post-verification GET %s → status=%s, final_url=%s", original_url, status, final_url)
            return SimpleResponse(text=html, url=final_url, status_code=status)
        finally:
            page.close()

    def get(self, url, **kwargs) -> SimpleResponse:
        self._ensure_browser()
        page = self._context.new_page()
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            status = response.status if response else 0
            final_url = page.url
            html = page.content()
            logger.info("Playwright GET %s → status=%s, final_url=%s", url, status, final_url)

            if self._is_verification_redirect(final_url):
                page.close()
                return self._handle_verification(final_url, url)

            return SimpleResponse(text=html, url=final_url, status_code=status)
        finally:
            if not page.is_closed():
                page.close()

    def close(self):
        self._close_browser()

    def __del__(self):
        self.close()
