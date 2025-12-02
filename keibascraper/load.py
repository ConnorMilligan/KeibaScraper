# load.py

import time
import random
import requests
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

from keibascraper.helper import load_config
from keibascraper.parse import parse_html, parse_json


def load(data_type, entity_id):
    """
    Load data from netkeiba.com based on the specified data type and entity ID.
    """
    loaders = {
        'entry': EntryLoader,
        'odds': OddsLoader,
        'result': ResultLoader,
        'horse': HorseLoader,
    }

    loader_class = loaders.get(data_type)
    if not loader_class:
        raise ValueError(f"Unexpected data type: {data_type}")

    loader = loader_class(entity_id)
    return loader.load()

def race_list(year:int, month:int) -> list:
    """ collect arguments race id. """
    calc = CalendarLoader(year, month)
    return calc.load()

class BaseLoader:
    def __init__(self, entity_id):
        self.entity_id = entity_id

    def create_url(self, base_url):
        return base_url.replace('{ID}', self.entity_id)

    def load_contents(self, url):
        time.sleep(random.uniform(2, 3))
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/58.0.3029.110 Safari/537.3'
            )
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'EUC-JP'
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to load contents from {url}") from e

    def render_with_playwright(self, url, timeout=20000, wait_selector=None):
        """Render page with Playwright and return fully rendered HTML (after JS)."""
        if sync_playwright is None:
            raise RuntimeError(
                "Playwright not installed. Run: pip install playwright && python -m playwright install chromium"
            )
        time.sleep(random.uniform(2, 3))
        try:
            with sync_playwright() as p:
                # include no-sandbox flags for many Linux environments / containers
                browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/58.0.3029.110 Safari/537.3"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.set_default_navigation_timeout(timeout)
                page.goto(url, wait_until="networkidle", timeout=timeout)
                if wait_selector:
                    # wait for an element that the page's JS creates (pass a selector if known)
                    page.wait_for_selector(wait_selector, timeout=timeout)
                content = page.content()
                context.close()
                browser.close()
                return content
        except Exception as e:
            # persist full traceback to a file for debugging and re-raise with a clear message
            import traceback
            tb = traceback.format_exc()
            with open("playwright_error.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- Playwright error for {url} ---\n{tb}\n")
            raise RuntimeError(f"Failed to render page with Playwright for {url}: {e}") from e

    def parse_with_error_handling(self, parse_funcs):
        results = []
        for parse_func, args in parse_funcs:
            try:
                result = parse_func(*args)
                results.append(result)
            except RuntimeError as e:
                raise RuntimeError(f"Failed to parse data for {self.entity_id}: {e}") from e
        return results


class EntryLoader(BaseLoader):
    def load(self):
        config = load_config('entry')
        url = self.create_url(config['property']['url'])
        content = self.load_contents(url)

        parse_funcs = [
            (parse_html, ('race', content, self.entity_id)),
            (parse_html, ('entry', content, self.entity_id))
        ]
        race, entry = self.parse_with_error_handling(parse_funcs)

        return race, entry


class OddsLoader(BaseLoader):
    def load(self):
        config = load_config('odds')
        url = self.create_url(config['property']['url'])
        content = self.load_contents(url)

        parse_funcs = [
            (parse_json, ('odds', content, self.entity_id))
        ]
        odds_data, = self.parse_with_error_handling(parse_funcs)
        return odds_data


class ResultLoader(BaseLoader):
    def load(self):
        config = load_config('result')
        url = self.create_url(config['property']['url'])
        content = self.load_contents(url)

        parse_funcs = [
            (parse_html, ('race_db', content, self.entity_id)),
            (parse_html, ('result', content, self.entity_id))
        ]
        race, entry = self.parse_with_error_handling(parse_funcs)

        return race, entry


class HorseLoader(BaseLoader):
    def load(self):
        config = load_config('horse')
        url = self.create_url(config['property']['url'])
        # use a JS renderer because the horse page is generated by client-side JS
        try:
            # If you know a selector that only appears after JS runs, pass it as wait_selector.
            # e.g. wait_selector='.HorseData' (replace with real selector) to be stricter.
            content = self.render_with_playwright(url, wait_selector=None, timeout=30000)
        except RuntimeError as e:
            # Log the Playwright failure and fallback so you can inspect playwright_error.log
            print(f"Playwright render failed: {e}. Falling back to requests for horse page.")
            content = self.load_contents(url)
        
        # write content to a file for debugging
        #with open(f"horse_{self.entity_id}.html", "w", encoding="utf-8") as f:
        #    f.write(content)

        parse_funcs = [
            (parse_html, ('horse', content, self.entity_id)),
            (parse_html, ('history', content, self.entity_id))
        ]
        horse, history = self.parse_with_error_handling(parse_funcs)
        #print(horse)
        #print(history[0])

        return horse, history


class CalendarLoader:
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def load(self):
        url = f"https://sports.yahoo.co.jp/keiba/schedule/monthly?year={self.year}&month={self.month}"
        print(url)
        content = self.load_contents(url)
        race_ids = parse_html('cal', content)
                # write content to a file for debugging
        with open(f"calendar_{self.year}_{self.month}.html", "w", encoding="utf-8") as f:
            f.write(content)
        return self.expand_race_ids(race_ids)

    def load_contents(self, url):
        try:
            response = requests.get(url)
            response.encoding = 'EUC-JP'
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to load contents from {url}") from e
    
    def expand_race_ids(self, input_data):
        race_ids = []
        for item in input_data:
            race_id = item.get('race_id')
            if not race_id:
                print(f"Warning: Item {item} does not contain 'race_id'. Skipping.")
                continue
            
            if len(race_id) == 8:
                base_id = '20' + race_id
                expanded_ids = [f"{base_id}{str(i).zfill(2)}" for i in range(1, 13)]
                race_ids.extend(expanded_ids)
            else:
                print(f"Warning: race_id '{race_id}' has invalid length ({len(race_id)}). Skipping.")
        
        return race_ids
