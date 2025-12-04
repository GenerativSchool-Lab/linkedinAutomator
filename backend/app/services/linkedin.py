import asyncio
import json
import os
from pathlib import Path
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from cryptography.fernet import Fernet
from app.config import settings


class LinkedInService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.cookies_dir = Path(".cookies")
        self.cookies_dir.mkdir(exist_ok=True)
        self.cookies_file = self.cookies_dir / "linkedin_cookies.json"
        self._cipher = None

    def _get_cipher(self):
        """Get or create encryption cipher for cookies"""
        if self._cipher is None:
            key = settings.secret_key.encode()[:32].ljust(32, b'0')
            from base64 import urlsafe_b64encode
            key = urlsafe_b64encode(key)
            self._cipher = Fernet(key)
        return self._cipher

    async def start_browser(self):
        """Start browser and load session"""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
            )
            self.page = await self.context.new_page()

            # Load cookies if they exist
            if self.cookies_file.exists():
                try:
                    cipher = self._get_cipher()
                    encrypted = self.cookies_file.read_bytes()
                    decrypted = cipher.decrypt(encrypted)
                    cookies = json.loads(decrypted.decode())
                    await self.context.add_cookies(cookies)
                except Exception as e:
                    print(f"Error loading cookies: {e}")

    async def login(self, email: Optional[str] = None, password: Optional[str] = None):
        """Login to LinkedIn"""
        await self.start_browser()
        
        email = email or settings.linkedin_email
        password = password or settings.linkedin_password

        if not email or not password:
            raise ValueError("LinkedIn email and password are required")

        await self.page.goto("https://www.linkedin.com/login")
        await asyncio.sleep(2)

        # Fill login form
        await self.page.fill('input[name="session_key"]', email)
        await self.page.fill('input[name="session_password"]', password)
        await self.page.click('button[type="submit"]')
        
        # Wait for navigation
        await self.page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(3)

        # Check if login was successful
        if "feed" in self.page.url or "linkedin.com/in/" in self.page.url:
            # Save cookies
            cookies = await self.context.cookies()
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(json.dumps(cookies).encode())
            self.cookies_file.write_bytes(encrypted)
            return True
        else:
            # Check for error messages
            error = await self.page.query_selector('.alert-content')
            if error:
                error_text = await error.text_content()
                raise Exception(f"Login failed: {error_text}")
            raise Exception("Login failed: Unknown error")

    async def ensure_logged_in(self):
        """Ensure we're logged in, redirect to login if not"""
        await self.start_browser()
        await self.page.goto("https://www.linkedin.com/feed")
        await asyncio.sleep(2)

        # Check if we're logged in
        if "login" in self.page.url:
            if settings.linkedin_email and settings.linkedin_password:
                await self.login()
            else:
                raise Exception("Not logged in and no credentials provided")

    async def send_connection_request(self, profile_url: str, message: str) -> tuple[bool, str | None]:
        """
        Send a connection request with a message
        
        Returns:
            Tuple of (success: bool, failure_reason: str | None)
        """
        await self.ensure_logged_in()
        
        try:
            # Navigate to profile
            await self.page.goto(profile_url)
            await asyncio.sleep(3)

            # Check if already connected (Message button indicates connection)
            if await self.page.query_selector('button:has-text("Message")'):
                return (True, None)  # Already connected, consider it success
            
            # Check for "Pending" status
            pending_indicator = await self.page.query_selector('button:has-text("Pending"), span:has-text("Pending")')
            if pending_indicator:
                return (False, "Connection request already pending")

            # Look for Connect button
            connect_button = await self.page.query_selector('button:has-text("Connect")')
            if not connect_button:
                # Try alternative selectors
                connect_button = await self.page.query_selector('button[aria-label*="Connect"]')
            
            if not connect_button:
                # Check for "Follow" button (can't connect, only follow)
                follow_button = await self.page.query_selector('button:has-text("Follow")')
                if follow_button:
                    return (False, "Profile only allows following, not connecting")
                
                # Check if profile is restricted
                restricted = await self.page.query_selector('.profile-unavailable, .restricted-profile')
                if restricted:
                    return (False, "Profile is restricted or unavailable")
                
                return (False, "Connect button not found - profile may be restricted or connection not available")

            await connect_button.click()
            await asyncio.sleep(2)

            # Check if a modal appeared asking for connection type
            # Sometimes LinkedIn asks "How do you know this person?"
            modal = await self.page.query_selector('.artdeco-modal, .connection-request-modal')
            if modal:
                # Try to close or select "I don't know" option
                close_button = await self.page.query_selector('button[aria-label*="Dismiss"], button:has-text("Skip")')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(1)

            # Look for "Add a note" button or message field
            add_note = await self.page.query_selector('button:has-text("Add a note")')
            if add_note:
                await add_note.click()
                await asyncio.sleep(1)

            # Find message textarea
            message_field = await self.page.query_selector('textarea[name="message"]')
            if not message_field:
                message_field = await self.page.query_selector('textarea[placeholder*="message"]')
            
            if message_field:
                await message_field.fill(message)
                await asyncio.sleep(1)
            else:
                # Message field not found, but connection might still work
                print("Warning: Message field not found, but continuing...")

            # Click Send button
            send_button = await self.page.query_selector('button:has-text("Send")')
            if not send_button:
                send_button = await self.page.query_selector('button[aria-label*="Send"]')
            
            if send_button:
                await send_button.click()
                await asyncio.sleep(2)
                
                # Check if there was an error message
                error_message = await self.page.query_selector('.artdeco-inline-feedback--error, .error-message')
                if error_message:
                    error_text = await error_message.text_content()
                    return (False, f"LinkedIn error: {error_text.strip()}")
                
                return (True, None)
            else:
                return (False, "Send button not found")

        except Exception as e:
            error_msg = str(e)
            # Categorize common errors
            if "login" in error_msg.lower() or "authentication" in error_msg.lower():
                return (False, "Login/authentication failed")
            elif "timeout" in error_msg.lower() or "network" in error_msg.lower():
                return (False, "Network timeout or connection error")
            elif "not found" in error_msg.lower():
                return (False, f"Profile or element not found: {error_msg}")
            else:
                return (False, f"Error: {error_msg}")

    async def send_message(self, profile_url: str, message: str) -> bool:
        """Send a message to an existing connection"""
        await self.ensure_logged_in()
        
        try:
            # Navigate to profile
            await self.page.goto(profile_url)
            await asyncio.sleep(3)

            # Click Message button
            message_button = await self.page.query_selector('button:has-text("Message")')
            if not message_button:
                raise Exception("Message button not found - not connected?")

            await message_button.click()
            await asyncio.sleep(2)

            # Find message input
            message_input = await self.page.query_selector('div[contenteditable="true"][role="textbox"]')
            if not message_input:
                message_input = await self.page.query_selector('textarea[placeholder*="message"]')
            
            if not message_input:
                raise Exception("Message input not found")

            await message_input.fill(message)
            await asyncio.sleep(1)

            # Click Send button
            send_button = await self.page.query_selector('button[aria-label*="Send"]')
            if not send_button:
                send_button = await self.page.query_selector('button:has-text("Send")')
            
            if send_button:
                await send_button.click()
                await asyncio.sleep(2)
                return True
            else:
                raise Exception("Send button not found")

        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    async def scrape_profile_details(self, profile_url: str) -> dict:
        """
        Scrape detailed information from a LinkedIn profile page
        
        Args:
            profile_url: Full LinkedIn profile URL
            
        Returns:
            Dictionary with profile details (headline, about, experience, etc.)
        """
        await self.ensure_logged_in()
        
        try:
            await self.page.goto(profile_url)
            await asyncio.sleep(3)
            
            profile_data = {
                'linkedin_url': profile_url,
                'name': None,
                'headline': None,
                'about': None,
                'location': None,
                'current_company': None,
                'current_title': None,
                'experience': [],
            }
            
            # Extract name
            try:
                name_elem = await self.page.query_selector('h1.text-heading-xlarge, h1.pv-text-details__left-panel h1')
                if name_elem:
                    name_text = await name_elem.text_content()
                    if name_text:
                        profile_data['name'] = name_text.strip()
            except:
                pass
            
            # Extract headline
            try:
                headline_elem = await self.page.query_selector('.text-body-medium.break-words, .pv-text-details__left-panel .text-body-medium')
                if headline_elem:
                    headline_text = await headline_elem.text_content()
                    if headline_text:
                        profile_data['headline'] = headline_text.strip()
            except:
                pass
            
            # Extract about section
            try:
                about_section = await self.page.query_selector('#about ~ .pvs-list, section[data-section="summary"]')
                if about_section:
                    about_text = await about_section.text_content()
                    if about_text:
                        profile_data['about'] = about_text.strip()[:500]  # Limit length
            except:
                pass
            
            # Extract location
            try:
                location_elem = await self.page.query_selector('.text-body-small.inline.t-black--light.break-words, .pv-text-details__left-panel .text-body-small')
                if location_elem:
                    location_text = await location_elem.text_content()
                    if location_text:
                        profile_data['location'] = location_text.strip()
            except:
                pass
            
            # Extract current experience
            try:
                experience_section = await self.page.query_selector('#experience ~ .pvs-list, section[data-section="experience"]')
                if experience_section:
                    # Get first (current) experience
                    first_exp = await experience_section.query_selector('.pvs-list__item')
                    if first_exp:
                        # Extract title
                        title_elem = await first_exp.query_selector('.mr1.t-bold span[aria-hidden="true"]')
                        if title_elem:
                            title_text = await title_elem.text_content()
                            if title_text:
                                profile_data['current_title'] = title_text.strip()
                        
                        # Extract company
                        company_elem = await first_exp.query_selector('.t-14.t-normal span[aria-hidden="true"]')
                        if company_elem:
                            company_text = await company_elem.text_content()
                            if company_text:
                                profile_data['current_company'] = company_text.strip()
            except:
                pass
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile details: {e}")
            return {'linkedin_url': profile_url}

    async def scrape_search_results(self, search_url: str, max_results: int = 50) -> List[dict]:
        """
        Scrape LinkedIn search results page and extract profile information
        
        Args:
            search_url: LinkedIn search URL (e.g., https://www.linkedin.com/search/results/people/...)
            max_results: Maximum number of profiles to scrape
            
        Returns:
            List of dictionaries with profile information
        """
        await self.ensure_logged_in()
        
        profiles = []
        try:
            # Navigate to search URL
            await self.page.goto(search_url)
            await asyncio.sleep(3)
            
            # Wait for search results to load
            await self.page.wait_for_selector('.reusable-search__result-container', timeout=10000)
            await asyncio.sleep(2)
            
            # Scroll to load more results
            scroll_count = 0
            max_scrolls = max_results // 10  # LinkedIn shows ~10 results per scroll
            
            while len(profiles) < max_results and scroll_count < max_scrolls:
                # Get all result containers
                result_containers = await self.page.query_selector_all('.reusable-search__result-container')
                
                for container in result_containers:
                    if len(profiles) >= max_results:
                        break
                    
                    try:
                        # Extract profile link
                        profile_link_elem = await container.query_selector('a.app-aware-link[href*="/in/"]')
                        if not profile_link_elem:
                            continue
                        
                        profile_url = await profile_link_elem.get_attribute('href')
                        if not profile_url or '/in/' not in profile_url:
                            continue
                        
                        # Make sure URL is complete
                        if not profile_url.startswith('http'):
                            profile_url = f"https://www.linkedin.com{profile_url.split('?')[0]}"
                        else:
                            profile_url = profile_url.split('?')[0]  # Remove query params
                        
                        # Extract name
                        name_elem = await container.query_selector('.entity-result__title-text a, .search-result__result-link')
                        name = "Unknown"
                        if name_elem:
                            name_text = await name_elem.text_content()
                            if name_text:
                                name = name_text.strip()
                        
                        # Extract title/headline
                        title_elem = await container.query_selector('.entity-result__primary-subtitle, .search-result__snippets')
                        title = None
                        if title_elem:
                            title_text = await title_elem.text_content()
                            if title_text:
                                title = title_text.strip()
                        
                        # Extract company (sometimes in subtitle)
                        company = None
                        if title and ' at ' in title:
                            parts = title.split(' at ')
                            if len(parts) > 1:
                                title = parts[0].strip()
                                company = parts[1].strip()
                        
                        # Skip if we already have this profile
                        if any(p.get('linkedin_url') == profile_url for p in profiles):
                            continue
                        
                        profiles.append({
                            'linkedin_url': profile_url,
                            'name': name,
                            'title': title,
                            'company': company,
                        })
                        
                    except Exception as e:
                        print(f"Error extracting profile from container: {e}")
                        continue
                
                # Scroll down to load more results
                if len(profiles) < max_results:
                    await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(2)
                    scroll_count += 1
                    
                    # Check if we've reached the end
                    try:
                        end_indicator = await self.page.query_selector('.search-results__end-of-results')
                        if end_indicator:
                            break
                    except:
                        pass
            
            return profiles[:max_results]
            
        except Exception as e:
            print(f"Error scraping search results: {e}")
            return profiles

    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        self.browser = None
        self.context = None
        self.page = None


# Global instance
linkedin_service = LinkedInService()




