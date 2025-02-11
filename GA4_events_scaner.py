import argparse
import json
import time
from typing import List, Dict
from urllib.parse import urlparse, parse_qs
import pandas as pd
import pytest
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def make_serializable(obj):
    """Recursively convert objects to serializable types."""
    if isinstance(obj, WebElement):
        try:
            return f"WebElement(tag={obj.tag_name}, text={obj.text})"
        except Exception:
            return "WebElement(unknown)"
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    else:
        return obj


def parse_ga4_event(event: Dict) -> Dict:
    """
    Parse a GA4 event message (from Chrome performance logs).
    First, check if the request has a URL with query parameters.
    If not, check if there's POST data and parse that.
    Extract parameters like 'ep.event_label' and 'ep.gtm_event'.
    """
    try:
        params = {}
        # First, try to parse query string from the URL
        request = event["params"]["request"]
        url = request.get("url", "")
        if url:
            parsed_url = urlparse(url)
            qs = parse_qs(parsed_url.query)
            params = qs
        
        # If no relevant parameter is found and there's POST data, parse it.
        if not params.get("ep.event_label") and "postData" in request:
            post_data = request["postData"]
            # postData might be URL-encoded string of parameters.
            qs_post = parse_qs(post_data)
            params = qs_post
        
        event_label = params.get("ep.event_label", [""])[0]
        gtm_event = params.get("ep.gtm_event", [""])[0]
        return {"event_label": event_label, "gtm_event": gtm_event, "url": url}
    except Exception as ex:
        return {"error": str(ex)}

class GA4EventCollector:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode.
        # Enable performance logging.
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.driver = webdriver.Chrome(options=chrome_options)
        self.events = []      # Captured dataLayer events.
        self.ga4_events = []  # Captured raw GA4 network events.
        self.inject_datalayer_collector()

    def inject_datalayer_collector(self):
        """Inject JavaScript to capture dataLayer.push calls into window.collectedEvents."""
        script = """
        window.collectedEvents = [];
        window.dataLayer = window.dataLayer || [];
        let originalPush = window.dataLayer.push;
        window.dataLayer.push = function() {
            const event = arguments[0];
            const cleanEvent = { timestamp: new Date().toISOString(), data: event };
            window.collectedEvents.push(cleanEvent);
            console.log('Captured dataLayer event:', cleanEvent);
            return originalPush.apply(this, arguments);
        };
        """
        self.driver.execute_script(script)

    def find_clickable_elements(self, section_selector="body"):
        """
        Find all visible clickable elements (buttons, anchors, spans) within the given section.
        """
        script = f"""
        function isVisible(el) {{
            if (!el) return false;
            if (!el.offsetParent) return false;
            if (el.offsetWidth === 0 || el.offsetHeight === 0) return false;
            const style = getComputedStyle(el);
            return !(style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0');
        }}
        let section = document.querySelector('{section_selector}');
        if (!section) return [];
        let elems = Array.from(section.querySelectorAll("button, a, span"));
        return elems.filter(isVisible);
        """
        return self.driver.execute_script(script)

    def get_element_info(self, element) -> dict:
        """Return details of an element."""
        return {
            'tag_name': element.tag_name,
            'text': element.text,
            'classes': element.get_attribute('class'),
            'href': element.get_attribute('href'),
            'data-target': element.get_attribute('data-target'),
            'data-link-type': element.get_attribute('data-link-type'),
            'aria-label': element.get_attribute('aria-label'),
            'target': element.get_attribute('target')
        }

    def wait_for_new_event(self, initial_count, timeout=5):
        """Wait until window.collectedEvents grows beyond initial_count."""
        start = time.time()
        while time.time() - start < timeout:
            events = self.get_collected_events()
            if len(events) > initial_count:
                return True
            time.sleep(0.5)
        return False

    def get_collected_events(self) -> List[Dict]:
        """Return collected dataLayer events."""
        events = self.driver.execute_script("return window.collectedEvents;")
        return events if events else []

    def get_ga4_events(self) -> List[Dict]:
        """
        Retrieve GA4 network events from performance logs.
        Filters for requests where URL contains 'g/collect' or 'mp/collect'.
        """
        logs = self.driver.get_log("performance")
        ga4_events = []
        for entry in logs:
            try:
                message = json.loads(entry["message"])["message"]
                if message.get("method") == "Network.requestWillBeSent":
                    url = message["params"]["request"]["url"]
                    if "g/collect" in url or "mp/collect" in url:
                        ga4_events.append(message)
            except Exception:
                continue
        return ga4_events

    def intercept_navigation(self):
        """
        Inject JavaScript to prevent default navigation (for testing).
        This ensures network logs remain on the same page.
        """
        script = """
        document.addEventListener('click', function(e) {
            var target = e.target.closest('a');
            if(target && target.href) {
                e.preventDefault();
                console.log('Navigation prevented for testing. Link:', target.href);
            }
        }, true);
        """
        self.driver.execute_script(script)

    def trigger_target_elements(self, section_selector="body", target_text=None):
        """
        Filter clickable elements by target_text (if provided) or by class substring.
        For each filtered element, click it and capture dataLayer and GA4 events.
        Returns a tuple: (dataLayer_events, ga4_events).
        """
        captured_dl_events = []
        captured_ga4_events = []
        elements = self.find_clickable_elements(section_selector)
        print(f"Found {len(elements)} clickable elements")
        
        snippets = ["primary-link icon-dx-search-inventory", "cta-content", "secondary-link", "cta"]
        filtered_elements = []
        for el in elements:
            info = self.get_element_info(el)
            if target_text:
                if info.get('text') and target_text.upper() in info.get('text').upper():
                    filtered_elements.append(el)
                    continue
            class_attr = el.get_attribute("class") or ""
            for snippet in snippets:
                if snippet in class_attr:
                    filtered_elements.append(el)
                    break

        if not filtered_elements:
            print("No matching elements found for given criteria.")
            return (captured_dl_events, captured_ga4_events)

        # Prevent navigation so that we can capture network logs.
        self.intercept_navigation()

        for target_element in filtered_elements:
            info = self.get_element_info(target_element)
            print(f"\nClicking target element: {info}")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(target_element))
                initial_dl_count = len(self.get_collected_events())
                initial_ga4_count = len(self.get_ga4_events())
                self.driver.execute_script("arguments[0].click();", target_element)
                time.sleep(3)  # Allow time for events to be sent.
                if self.wait_for_new_event(initial_dl_count, timeout=5):
                    new_dl = self.get_collected_events()[initial_dl_count:]
                    print("Captured new dataLayer event(s):", new_dl)
                    captured_dl_events.extend(new_dl)
                else:
                    print("No new dataLayer event detected after click.")
                new_ga4 = self.get_ga4_events()[initial_ga4_count:]
                if new_ga4:
                    print("Captured new GA4 network event(s):", new_ga4)
                    captured_ga4_events.extend(new_ga4)
                else:
                    print("No new GA4 network requests detected after click.")
            except Exception as e:
                print(f"Error during click on element: {str(e)}")
        return (captured_dl_events, captured_ga4_events)

    def collect_events_from_url(self, url: str, wait_time: int = 5, section_selector="body", target_text=None):
        """
        Load the URL, wait for the page to load, trigger clicks on target elements,
        and capture both dataLayer and GA4 events.
        """
        try:
            self.driver.get(url)
            print(f"Loaded URL: {url}")
            WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.inject_datalayer_collector()
            dl_events, ga4_events = self.trigger_target_elements(section_selector, target_text=target_text)
            self.events.extend(dl_events)
            self.ga4_events.extend(ga4_events)
            print(f"DataLayer events collected: {self.events}")
            print(f"GA4 events collected: {self.ga4_events}")
            return {"dataLayer": self.events, "ga4": self.ga4_events}
        except Exception as e:
            print(f"Error collecting events: {str(e)}")
            return {"dataLayer": [], "ga4": []}

    def export_events(self, filename: str):
        """
        Export dataLayer events and parsed GA4 events to separate files.
        For GA4 events, we parse the URL to extract, for example, event_label.
        """
        # Export dataLayer events.
        dl_serializable = make_serializable(self.events)
        with open(f"{filename}_dataLayer.json", 'w', encoding='utf-8') as f:
            json.dump(dl_serializable, f, indent=2, ensure_ascii=False)
        df_dl = pd.DataFrame(dl_serializable)
        df_dl.to_csv(f"{filename}_dataLayer.csv", index=False)

        # Parse GA4 events.
        parsed_ga4 = []
        for event in self.ga4_events:
            parsed = parse_ga4_event(event)
            parsed_ga4_entry = parsed.copy()
            # Optionally, include the timestamp from the raw event.
            parsed_ga4_entry["timestamp"] = event.get("timestamp")
            parsed_ga4.append(parsed_ga4_entry)

        with open(f"{filename}_GA4.json", 'w', encoding='utf-8') as f:
            json.dump(parsed_ga4, f, indent=2, ensure_ascii=False)
        df_ga4 = pd.DataFrame(parsed_ga4)
        df_ga4.to_csv(f"{filename}_GA4.csv", index=False)

    def close(self):
        """Close the browser."""
        self.driver.quit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='GA4 Events Scanner')
    parser.add_argument('--url', type=str, required=True, help='URL to scan')
    parser.add_argument('--section-selector', type=str, default='body', help='CSS selector for the section to scan')
    parser.add_argument('--target-text', type=str, default='', help='Filter by target text (optional)')
    parser.add_argument('--wait-time', type=int, default=5, help='Wait time for page load in seconds')
    return parser.parse_args()
# Pytest Tests
# -----------------------

@pytest.fixture(scope="module")
def collector():
    col = GA4EventCollector()
    yield col
    col.close()


def test_find_clickable_elements(collector):
    collector.driver.get("https://www.rangerover.com/de-de/range-rover/index.html")
    elements = collector.find_clickable_elements("body")
    assert len(elements) > 0, "No clickable elements found."
    for el in elements:
        tag = el.tag_name.lower()
        assert tag in ["button", "a", "span"], f"Unexpected tag: {tag}"


def test_filter_elements(collector):
    collector.driver.get("https://www.rangerover.com/de-de/range-rover/index.html")
    elements = collector.find_clickable_elements("body")
    filtered = []
    snippets = ["primary-link icon-dx-search-inventory", "cta-content", "secondary-link", "cta"]
    for el in elements:
        class_attr = el.get_attribute("class") or ""
        for snippet in snippets:
            if snippet in class_attr:
                filtered.append(el)
                break
    assert len(filtered) > 0, "No elements match the class criteria."


def test_click_generates_ga4_event(collector):
    collector.driver.get("https://www.rangerover.com/de-de/range-rover/index.html")
    initial_ga4 = len(collector.get_ga4_events())
    _, captured_ga4 = collector.trigger_target_elements("body", target_text=None)
    time.sleep(3)
    new_ga4 = collector.get_ga4_events()
    assert len(new_ga4) > initial_ga4, "Click did not generate a new GA4 network event."
    assert len(captured_ga4) > 0, "No GA4 events were captured during clicks."


# -----------------------
# Main Execution
# -----------------------

if __name__ == "__main__":
    args = parse_arguments()
    collector = GA4EventCollector()
    try:
        events = collector.collect_events_from_url(
            url=args.url,
            section_selector=args.section_selector,
            target_text=args.target_text,
            wait_time=args.wait_time
        )
        sanitized_url = sanitize_url(args.url)
        collector.export_events(f"data_to_analysis/output_data/{sanitized_url}/gtm_and_ga4_events")
        print(f"\nCollected dataLayer events: {len(events['dataLayer'])}")
        print(f"Collected GA4 events: {len(events['ga4'])}")
    finally:
        collector.close()
