import asyncio
import re
import time
import urllib.parse
import threading
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

def clean_str(s):
    if not s:
        return "Not Available"
    s = re.sub(r'[\r\n\t]+', ' ', str(s)).strip()
    return s if s else "Not Available"

def parse_address(addr_str):
    if not addr_str or addr_str == 'Not Available':
        return {'city': 'Not Available', 'state': 'Not Available', 'country': 'Not Available'}
        
    cleaned = re.sub(r'[\r\n\t]+', ' ', addr_str).strip()
    cleaned = re.sub(r'^Address:\s*', '', cleaned, flags=re.I)
    cleaned = re.sub(r'[\ue000-\uf8ff]', '', cleaned).strip()  # remove private unicode icons
    
    parts = [p.strip() for p in cleaned.split(',') if p.strip()]
    city = 'Not Available'
    state = 'Not Available'
    country = 'USA'
    
    if len(parts) >= 3:
        if parts[-1].lower() in ['usa', 'united states', 'united states of america']:
            country = parts[-1]
            state_zip_part = parts[-2]
            city_part = parts[-3]
        else:
            state_zip_part = parts[-1]
            city_part = parts[-2]
            
        m = re.search(r'\b([A-Z]{2})\b(?:\s+(\d{5}(?:-\d{4})?))?', state_zip_part)
        if m:
            state = m.group(1)
        else:
            state = state_zip_part.strip()
        city = city_part
    elif len(parts) == 2:
        city = parts[0]
        m = re.search(r'\b([A-Z]{2})\b', parts[1])
        state = m.group(1) if m else parts[1].strip()
    elif len(parts) == 1:
        city = parts[0]
        
    return {
        'city': clean_str(city),
        'state': clean_str(state),
        'country': clean_str(country)
    }

def fetch_email_from_website(website_url):
    """Fast synchronous extraction of public email address from business website"""
    if not website_url or website_url == 'Not Available' or not website_url.startswith('http'):
        return 'Not Available'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    
    def check_url(target_url):
        try:
            resp = requests.get(target_url, headers=headers, timeout=3.5, verify=False)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # 1. Look for mailto:
                for a in soup.find_all('a', href=True):
                    href = a['href'].strip()
                    if href.lower().startswith('mailto:'):
                        em = href.replace('mailto:', '').split('?')[0].strip()
                        if '@' in em and '.' in em:
                            return em
                # 2. Look for regex emails in page text
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)
                for e in emails:
                    low = e.lower()
                    if not any(low.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.js', '.css']):
                        if 'sentry' not in low and 'wix' not in low and 'schema.org' not in low and 'example.com' not in low:
                            return e
        except Exception:
            pass
        return None

    # Try homepage
    email = check_url(website_url)
    if email:
        return email
        
    # If not found, try /contact
    base = website_url.rstrip('/')
    if not base.endswith('/contact') and not base.endswith('/about'):
        contact_email = check_url(base + '/contact')
        if contact_email:
            return contact_email
            
    return 'Not Available'


class ScraperController:
    """Thread-safe controller for the Google Maps automation pipeline"""
    def __init__(self):
        self.lock = threading.Lock()
        self.state = "idle"  # idle, running, paused, completed, stopped, error
        self.pause_event = None
        self.stop_requested = False
        self.loop = None
        self.thread = None
        
        # Metrics & Data
        self.services = []
        self.locations = []
        self.combinations = []
        self.total_combinations = 0
        self.current_combination_idx = 0
        self.current_service = ""
        self.current_location = ""
        self.current_business_name = ""
        
        self.max_results_per_search = 25
        self.remove_duplicates = True
        
        self.businesses_found = 0
        self.businesses_processed = 0
        self.businesses_remaining = 0
        self.progress_percent = 0.0
        self.status_message = "Ready to start."
        
        self.businesses = []
        self._seen_map = {}  # for duplicate detection

    def get_snapshot(self):
        with self.lock:
            return {
                "state": self.state,
                "total_combinations": self.total_combinations,
                "current_combination_idx": self.current_combination_idx,
                "current_service": self.current_service,
                "current_location": self.current_location,
                "current_business_name": self.current_business_name,
                "businesses_found": self.businesses_found,
                "businesses_processed": self.businesses_processed,
                "businesses_remaining": self.businesses_remaining,
                "progress_percent": round(self.progress_percent, 1),
                "status_message": self.status_message,
                "total_collected": len(self.businesses),
                "businesses": list(self.businesses)
            }

    def start_job(self, services, locations, max_results=25, remove_duplicates=True):
        with self.lock:
            if self.state in ["running", "paused"]:
                return False, "A job is already running or paused."
            
            self.services = [s.strip() for s in services if s.strip()]
            self.locations = [l.strip() for l in locations if l.strip()]
            
            if not self.services or not self.locations:
                return False, "Please provide at least one service and one location."
                
            self.combinations = [
                (s, l) for s in self.services for l in self.locations
            ]
            self.total_combinations = len(self.combinations)
            self.current_combination_idx = 0
            self.max_results_per_search = int(max_results)
            self.remove_duplicates = bool(remove_duplicates)
            
            self.businesses_found = 0
            self.businesses_processed = 0
            self.businesses_remaining = 0
            self.progress_percent = 0.0
            self.businesses = []
            self._seen_map = {}
            self.state = "running"
            self.stop_requested = False
            self.status_message = "Starting automation job..."

        # Start worker thread
        self.thread = threading.Thread(target=self._run_thread, daemon=True)
        self.thread.start()
        return True, "Job started successfully."

    def pause(self):
        with self.lock:
            if self.state != "running":
                return False, f"Cannot pause from state '{self.state}'"
            self.state = "paused"
            self.status_message = "Process paused by user."
            if self.pause_event and self.loop:
                self.loop.call_soon_threadsafe(self.pause_event.clear)
            return True, "Paused."

    def resume(self):
        with self.lock:
            if self.state != "paused":
                return False, f"Cannot resume from state '{self.state}'"
            self.state = "running"
            self.status_message = "Process resumed."
            if self.pause_event and self.loop:
                self.loop.call_soon_threadsafe(self.pause_event.set)
            return True, "Resumed."

    def stop(self):
        with self.lock:
            if self.state in ["idle", "completed", "stopped"]:
                return False, "No active job to stop."
            self.stop_requested = True
            self.state = "stopped"
            self.status_message = "Stopping process..."
            if self.pause_event and self.loop:
                self.loop.call_soon_threadsafe(self.pause_event.set)
            return True, "Stopped. Current data preserved."

    def _run_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._execute_pipeline())
        except Exception as e:
            with self.lock:
                self.state = "error"
                self.status_message = f"Error: {str(e)}"
        finally:
            self.loop.close()

    async def _check_pause_and_stop(self):
        """Awaits if paused, raises asyncio.CancelledError if stopped"""
        if self.stop_requested:
            raise asyncio.CancelledError("Stop requested by user")
        if self.pause_event:
            await self.pause_event.wait()
        if self.stop_requested:
            raise asyncio.CancelledError("Stop requested by user")

    def _normalize_phone(self, p):
        return re.sub(r'\D', '', str(p or ''))

    def _handle_duplicate_and_add(self, item):
        """Handles duplicate detection and merging"""
        with self.lock:
            url = item.get("url", "")
            phone = self._normalize_phone(item.get("phone", ""))
            name_addr = f"{item.get('name', '').lower()}_{item.get('address', '').lower()}"
            
            existing_idx = None
            if self.remove_duplicates:
                if url and url in self._seen_map:
                    existing_idx = self._seen_map[url]
                elif phone and len(phone) >= 7 and phone in self._seen_map:
                    existing_idx = self._seen_map[phone]
                elif name_addr and len(name_addr) > 5 and name_addr in self._seen_map:
                    existing_idx = self._seen_map[name_addr]

            if existing_idx is not None:
                # Merge service and location
                existing_item = self.businesses[existing_idx]
                srv = item.get("searchService", "")
                loc = item.get("searchLocation", "")
                
                curr_srvs = [s.strip() for s in existing_item.get("searchService", "").split(",") if s.strip()]
                if srv and srv not in curr_srvs:
                    curr_srvs.append(srv)
                    existing_item["searchService"] = ", ".join(curr_srvs)
                    
                curr_locs = [l.strip() for l in existing_item.get("searchLocation", "").split(",") if l.strip()]
                if loc and loc not in curr_locs:
                    curr_locs.append(loc)
                    existing_item["searchLocation"] = ", ".join(curr_locs)
                return False, existing_item
            else:
                idx = len(self.businesses)
                self.businesses.append(item)
                if url:
                    self._seen_map[url] = idx
                if phone and len(phone) >= 7:
                    self._seen_map[phone] = idx
                if name_addr and len(name_addr) > 5:
                    self._seen_map[name_addr] = idx
                return True, item

    async def _process_place_page(self, context, place_url, feed_name, service, location):
        """Processes a single business place profile page"""
        await self._check_pause_and_stop()
        page = await context.new_page()
        try:
            await page.goto(place_url, wait_until="domcontentloaded", timeout=18000)
            await page.wait_for_timeout(1000)
            
            data = await page.evaluate(r'''() => {
                const res = {};
                // Name
                const h1 = document.querySelector('h1');
                res.name = h1 ? h1.innerText.trim() : '';

                // Category
                const catBtn = document.querySelector('button[jsaction*="category"]');
                res.category = catBtn ? catBtn.innerText.trim() : '';

                // Rating
                const ratingEl = document.querySelector('div[role="img"][aria-label*="star"], span[aria-label*="star"]');
                if (ratingEl) {
                    const aria = ratingEl.getAttribute('aria-label') || '';
                    const match = aria.match(/([\d.]+)\s*star/i);
                    res.rating = match ? match[1] : aria.split(' ')[0];
                } else {
                    res.rating = '';
                }

                // Reviews
                const reviewsEl = document.querySelector('span[aria-label*="reviews"], button[aria-label*="reviews"]');
                if (reviewsEl) {
                    const match = (reviewsEl.getAttribute('aria-label') || '').match(/[\d,]+/);
                    res.reviews = match ? match[0].replace(/,/g, '') : '';
                } else {
                    res.reviews = '';
                }

                // Address
                const addrEl = document.querySelector('button[data-item-id="address"], button[aria-label*="Address:" i], [data-tooltip="Copy address"]');
                let addr = '';
                if (addrEl) {
                    addr = addrEl.getAttribute('aria-label') || addrEl.innerText;
                    addr = addr.replace(/^Address:\s*/i, '').trim();
                }
                res.address = addr;

                // Website
                const webEl = document.querySelector('a[data-item-id="authority"], a[aria-label*="Website:" i], a[aria-label="Open website"]');
                res.website = webEl ? (webEl.getAttribute('href') || '') : '';

                // Phone
                const phoneEl = document.querySelector('button[data-item-id*="phone:"], button[aria-label*="Phone:" i], [data-tooltip="Copy phone number"]');
                let phone = '';
                if (phoneEl) {
                    phone = phoneEl.getAttribute('aria-label') || phoneEl.innerText;
                    phone = phone.replace(/^Phone:\s*/i, '').trim();
                }
                res.phone = phone;

                // Claim status check:
                // Look for "Claim this business" or "Own this business?"
                const claimLink = document.querySelector('a[href*="claim"], a[href*="business.google.com"], button[aria-label*="Claim this business" i], a[aria-label*="Claim this business" i], [data-item-id="merchant"]');
                const bodyText = document.body ? document.body.innerText : '';
                const hasClaimText = bodyText.includes('Claim this business') || bodyText.includes('Own this business?');

                if (claimLink || hasClaimText) {
                    res.claimStatus = 'Available';
                } else {
                    res.claimStatus = 'Not Available';
                }

                return res;
            }''')

            # Clean and format
            name = clean_str(data.get("name") or feed_name)
            category = clean_str(data.get("category"))
            rating = clean_str(data.get("rating"))
            reviews = clean_str(data.get("reviews"))
            address = clean_str(data.get("address"))
            phone = clean_str(data.get("phone"))
            website = clean_str(data.get("website"))
            claim_status = clean_str(data.get("claimStatus") or "Not Available")
            
            # Parse City, State, Country
            geo = parse_address(address)
            
            # Fetch public email if website is present
            email = "Not Available"
            if website and website != "Not Available":
                # Run email fetcher in thread to keep async event loop non-blocking
                email = await asyncio.to_thread(fetch_email_from_website, website)
                
            item = {
                "name": name,
                "category": category,
                "website": website,
                "email": clean_str(email),
                "phone": phone,
                "address": address,
                "city": geo["city"],
                "state": geo["state"],
                "country": geo["country"],
                "url": place_url,
                "rating": rating,
                "reviews": reviews,
                "claimStatus": claim_status,
                "searchService": service,
                "searchLocation": location
            }
            
            return item
        except Exception as e:
            # Fallback entry to maintain data integrity
            geo = parse_address("Not Available")
            return {
                "name": clean_str(feed_name),
                "category": "Not Available",
                "website": "Not Available",
                "email": "Not Available",
                "phone": "Not Available",
                "address": "Not Available",
                "city": geo["city"],
                "state": geo["state"],
                "country": geo["country"],
                "url": place_url,
                "rating": "Not Available",
                "reviews": "Not Available",
                "claimStatus": "Not Available",
                "searchService": service,
                "searchLocation": location
            }
        finally:
            await page.close()

    async def _execute_pipeline(self):
        self.pause_event = asyncio.Event()
        self.pause_event.set()
        
        async with async_playwright() as p:
            # Launch Chrome with English locale for consistent selectors
            browser = await p.chromium.launch(
                channel="chrome",
                headless=True,
                args=["--lang=en-US", "--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                locale="en-US",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

            try:
                for idx, (service, location) in enumerate(self.combinations, start=1):
                    await self._check_pause_and_stop()
                    
                    with self.lock:
                        self.current_combination_idx = idx
                        self.current_service = service
                        self.current_location = location
                        self.status_message = f"Searching: {service} in {location} ({idx} / {self.total_combinations})"
                        self.progress_percent = ((idx - 1) / self.total_combinations) * 100

                    # 1. Search Google Maps
                    query = f"{service} in {location}"
                    search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}?hl=en"
                    
                    search_page = await context.new_page()
                    try:
                        await search_page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
                        
                        # Wait for feed or place links
                        try:
                            await search_page.wait_for_selector('a[href*="/maps/place"]', timeout=12000)
                        except Exception:
                            # Might be single exact business page or no results
                            pass

                        # Feed scroll loop
                        collected_feed_items = []
                        seen_hrefs = set()
                        scroll_attempts = 0
                        # Dynamic max scrolls to easily support up to 1000 items
                        max_scrolls = max(20, (self.max_results_per_search // 5) + 15)
                        consecutive_stalls = 0

                        while len(collected_feed_items) < self.max_results_per_search and scroll_attempts < max_scrolls:
                            await self._check_pause_and_stop()
                            
                            prev_count = len(collected_feed_items)
                            # Grab current links
                            links = await search_page.locator('a[href*="/maps/place"]').all()
                            for l in links:
                                href = await l.get_attribute("href")
                                aria = await l.get_attribute("aria-label") or ""
                                if href and href not in seen_hrefs and "/maps/place/" in href:
                                    seen_hrefs.add(href)
                                    collected_feed_items.append({"url": href, "name": aria})
                                    if len(collected_feed_items) >= self.max_results_per_search:
                                        break
                                        
                            if len(collected_feed_items) >= self.max_results_per_search:
                                break
                                
                            # Check if new items loaded
                            if len(collected_feed_items) == prev_count:
                                consecutive_stalls += 1
                                if consecutive_stalls >= 5:
                                    # End of feed reached
                                    break
                            else:
                                consecutive_stalls = 0

                            # Check for "You've reached the end of the list"
                            end_text = await search_page.locator('text="You\'ve reached the end of the list"').count()
                            if end_text > 0:
                                break

                            # Scroll feed
                            feed = search_page.locator('div[role="feed"]').first
                            if await feed.count() > 0:
                                await search_page.evaluate('(f) => f.scrollBy(0, 1500)', await feed.element_handle())
                                await search_page.wait_for_timeout(700)
                            else:
                                break
                            scroll_attempts += 1
                    finally:
                        await search_page.close()

                    with self.lock:
                        found_count = len(collected_feed_items)
                        self.businesses_found += found_count
                        self.businesses_remaining = found_count
                        self.status_message = f"Found {found_count} businesses for '{service} in {location}'. Extracting details..."

                    # 2. Process place details with concurrency
                    sem = asyncio.Semaphore(4)  # 4 concurrent worker tabs for ultra-fast processing

                    async def worker(item_dict):
                        async with sem:
                            await self._check_pause_and_stop()
                            with self.lock:
                                self.current_business_name = item_dict.get("name", "Loading...")
                                self.status_message = f"Processing: {self.current_business_name}"
                            
                            biz_data = await self._process_place_page(
                                context, item_dict["url"], item_dict["name"], service, location
                            )
                            
                            self._handle_duplicate_and_add(biz_data)
                            
                            with self.lock:
                                self.businesses_processed += 1
                                if self.businesses_remaining > 0:
                                    self.businesses_remaining -= 1
                                # Sub-progress within this search
                                sub_pct = (self.businesses_processed / max(1, self.businesses_found))
                                base_pct = ((idx - 1) / self.total_combinations) * 100
                                step_pct = (1.0 / self.total_combinations) * 100
                                self.progress_percent = min(99.0, base_pct + (sub_pct * step_pct))

                    # Gather all place tasks
                    tasks = [worker(item) for item in collected_feed_items]
                    if tasks:
                        await asyncio.gather(*tasks)

                # Completed all combinations
                with self.lock:
                    self.state = "completed"
                    self.progress_percent = 100.0
                    self.status_message = f"Complete! Collected {len(self.businesses)} unique businesses across {self.total_combinations} combinations."
                    self.current_business_name = "Done"

            except asyncio.CancelledError:
                with self.lock:
                    self.state = "stopped"
                    self.status_message = f"Stopped. Collected {len(self.businesses)} businesses so far."
            except Exception as e:
                with self.lock:
                    self.state = "error"
                    self.status_message = f"Pipeline error: {str(e)}"
            finally:
                await browser.close()
