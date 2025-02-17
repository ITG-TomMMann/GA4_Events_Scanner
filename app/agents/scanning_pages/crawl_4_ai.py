
# GA4 Event Collector with Crawl4AI (Mimicking Selenium)
# =======================================================
#
# This script mimics the Selenium-based GA4 event collector using Crawl4AI.
# It injects JavaScript to capture dataLayer events and GA4 events (including POST bodies),
# stores the current page URL to ensure valid context for all JS executions,
# simulates user clicks to trigger further events, and finally displays both
# sets of events via a Streamlit interface.

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import json
import pandas as pd
import streamlit as st
from urllib.parse import urlparse, parse_qs
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ------------------------------------------------------------------
# Helper Function: Parse GA4 Event
# ------------------------------------------------------------------

def parse_ga4_event(event: dict) -> dict:
    """
    Parse a GA4 event to extract:
      - event_label
      - event_action
      - event_category
      - button_text (if provided)
    Merges URL query parameters and POST body parameters.
    """
    try:
        # Extract query parameters from the URL.
        url_val = event.get("url", "")
        query_params = {}
        if url_val:
            parsed_url = urlparse(url_val)
            query_params = parse_qs(parsed_url.query)
        
        # Extract parameters from the POST body if present.
        body_params = {}
        body_text = event.get("body", "") or ""
        if body_text:
            body_params = parse_qs(body_text)
        
        # Merge parameters (POST data takes precedence).
        merged = {**query_params, **body_params}
        
        event_label = merged.get("ep.event_label", [""])[0]
        event_action = merged.get("ep.event_action", [""])[0]
        event_category = merged.get("ep.event_category", [""])[0]
        button_text = event.get("button_text", "")
        
        return {
            "event_label": event_label,
            "event_action": event_action,
            "event_category": event_category,
            "button_text": button_text
        }
    except Exception as ex:
        return {"error": str(ex)}

# ------------------------------------------------------------------
# GA4EventCollector Class (Mimicking Selenium)
# ------------------------------------------------------------------

class GA4EventCollector:
    def __init__(self):
        # Configure the headless browser via Crawl4AI.
        self.browser_config = BrowserConfig(headless=True, verbose=True)
        
        # JavaScript override to capture dataLayer events.
        self.data_layer_override = r"""
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
        
        # Enhanced fetch override to capture GA4 events (including POST bodies).
        self.enhanced_fetch_override = r"""
        (function() {
            const originalFetch = window.fetch;
            window.ga4Events = window.ga4Events || [];
            window.fetch = async function(resource, init) {
                let clonedBody = "";
                if (init && init.body) {
                    if (typeof init.body === 'string') {
                        clonedBody = init.body;
                    } else if (init.body instanceof Blob) {
                        clonedBody = await init.body.text();
                    }
                    console.log("Captured fetch body:", clonedBody);
                }
                if (typeof resource === 'string' && (resource.includes('g/collect') || resource.includes('mp/collect'))) {
                    console.log("Intercepted GA4 fetch call:", resource, clonedBody);
                    window.ga4Events.push({
                        url: resource,
                        timestamp: new Date().toISOString(),
                        body: clonedBody
                    });
                }
                return originalFetch.apply(this, arguments);
            };
        })();
        """
        
        # Build the base run configuration with extended timeout settings.
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            page_timeout=60000,    # 60-second timeout
            wait_until="load",     # Wait for the load event
            js_code=[self.data_layer_override, self.enhanced_fetch_override]
        )
        
        self.crawler = AsyncWebCrawler(config=self.browser_config)
        self.current_url = ""  # Will store the current page URL after loading
    
    async def start(self):
        """Initialize the crawler (open browser context)."""
        await self.crawler.__aenter__()
    
    async def close(self):
        """Close the crawler and browser context."""
        await self.crawler.__aexit__(None, None, None)
    
    async def load_page(self, url: str):
        """
        Load the target page with injected JS and store the URL.
        Wait a few seconds to allow initial events to fire.
        """
        await self.crawler.arun(url=url, config=self.run_config)
        self.current_url = url
        await asyncio.sleep(5)
    
    async def run_js(self, script: str, session_id="session1"):
        """
        Run arbitrary JavaScript in the current page context using arun().
        Uses self.current_url as the URL context.
        """
        temp_config = self.run_config.clone()
        temp_config.js_code = [script]
        result = await self.crawler.arun(url=self.current_url, config=temp_config, session_id=session_id)
        return result.extracted_content
    
    async def get_data_layer_events(self, session_id="session1"):
        """
        Retrieve the dataLayer events captured on the page.
        """
        raw = await self.run_js("return JSON.stringify(window.collectedEvents);", session_id=session_id)
        if raw:
            return json.loads(raw)
        return []
    
    async def trigger_clicks(self, target_text=None, session_id="session1"):
        """
        Simulate clicks on visible elements. Optionally filter by target text.
        """
        condition = ("if (text && text.toUpperCase().includes('" + target_text.upper() + "')) { return true; } else " if target_text else "")
        js_click = r"""
        (function(){
            const elements = Array.from(document.querySelectorAll("button, a, span")).filter(el => {
                const style = window.getComputedStyle(el);
                if (style.visibility === 'hidden' || style.display === 'none' || parseFloat(style.opacity) === 0)
                    return false;
                const text = el.innerText || "";
                """ + condition + r"""
                return true;
            });
            console.log("Number of clickable elements:", elements.length);
            elements.forEach(el => {
                try {
                    el.scrollIntoView();
                    el.click();
                    console.log("Clicked element:", el);
                } catch(e) {
                    console.log("Error clicking element:", e);
                }
            });
        })();
        """
        await self.run_js(js_click, session_id=session_id)
        await asyncio.sleep(5)
    
    async def get_ga4_events(self, session_id="session1"):
        """
        Retrieve the GA4 events captured by the fetch override.
        """
        raw = await self.run_js("return JSON.stringify(window.ga4Events);", session_id=session_id)
        if raw:
            return json.loads(raw)
        return []

# ------------------------------------------------------------------
# Streamlit Interface
# ------------------------------------------------------------------

async def main():
    st.title("GA4 Event Collector (Mimicking Selenium)")
    st.write("Enter the URL from which to collect GA4 events.")
    
    url = st.text_input("URL", "https://www.rangerover.com/en-gb/range-rover/index.html")
    target_text = st.text_input("Target Text (optional)", "")
    
    if st.button("Collect GA4 Events"):
        if not url.strip():
            st.error("Please enter a valid URL.")
        else:
            url_cleaned = url.strip()
            st.write("DEBUG: URL to crawl:", url_cleaned)
            
            collector = GA4EventCollector()
            await collector.start()
            try:
                # Step 1: Load the page and capture initial dataLayer events.
                await collector.load_page(url_cleaned)
                dl_events = await collector.get_data_layer_events()
                st.subheader("DataLayer Events")
                st.json(dl_events)
                
                # Step 2: Simulate clicks to trigger additional GA4 events.
                await collector.trigger_clicks(target_text=target_text if target_text.strip() else None)
                ge_events = await collector.get_ga4_events()
                st.subheader("GA4 Events")
                st.json(ge_events)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                await collector.close()

if __name__ == "__main__":
    asyncio.run(main())
