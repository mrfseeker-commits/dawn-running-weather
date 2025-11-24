from playwright.sync_api import sync_playwright
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

def get_code_by_playwright(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        try:
            # Go to Naver Weather
            page.goto("https://weather.naver.com/", wait_until='domcontentloaded')
            
            # Click search button/input
            # The search input usually has id 'lnb_search' or similar class
            # Let's try to find the input by placeholder or selector
            
            # Wait for search input or button
            # Sometimes input is hidden behind a button
            try:
                # Try to find the input directly
                page.wait_for_selector("input.interest_form_input", state="attached", timeout=3000)
                
                # Check if visible
                if not page.is_visible("input.interest_form_input"):
                    # Click search button to reveal
                    # Try common selectors for search button
                    search_btn = page.query_selector("button[class*='search'], .btn_search, .button_search")
                    if search_btn:
                        search_btn.click()
                        page.wait_for_selector("input.interest_form_input", state="visible", timeout=3000)
            except:
                pass

            # Type query
            page.fill("input.interest_form_input", query)
            
            # Wait for autocomplete results
            page.wait_for_selector("a.interest_item_link", timeout=5000)
            
            # Click first result
            page.click("a.interest_item_link >> nth=0")
            
            # Wait for navigation
            page.wait_for_url("**/today/*", timeout=10000)
            
            current_url = page.url
            print(f"URL: {current_url}")
            
            # Extract code
            if "/today/" in current_url:
                code = current_url.split("/today/")[1].split("?")[0]
                return code
                
        except Exception as e:
            print(f"Error for {query}: {e}")
            # page.screenshot(path=f"error_{query}.png")
        finally:
            browser.close()
            
    return None

def test():
    queries = ["대전 목상동", "대전 송강동", "서울 강남역"]
    
    for q in queries:
        print(f"Searching for {q}...")
        code = get_code_by_playwright(q)
        print(f"Result: {code}")
        print("-" * 20)

if __name__ == "__main__":
    test()
