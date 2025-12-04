import asyncio
import json
import os
from pathlib import Path
from typing import Optional
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

    async def send_connection_request(self, profile_url: str, message: str) -> bool:
        """Send a connection request with a message"""
        await self.ensure_logged_in()
        
        try:
            # Navigate to profile
            await self.page.goto(profile_url)
            await asyncio.sleep(3)

            # Look for Connect button
            connect_button = await self.page.query_selector('button:has-text("Connect")')
            if not connect_button:
                # Try alternative selectors
                connect_button = await self.page.query_selector('button[aria-label*="Connect"]')
            
            if not connect_button:
                # Check if already connected
                if await self.page.query_selector('button:has-text("Message")'):
                    return True  # Already connected
                raise Exception("Connect button not found")

            await connect_button.click()
            await asyncio.sleep(2)

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

            # Click Send button
            send_button = await self.page.query_selector('button:has-text("Send")')
            if not send_button:
                send_button = await self.page.query_selector('button[aria-label*="Send"]')
            
            if send_button:
                await send_button.click()
                await asyncio.sleep(2)
                return True
            else:
                raise Exception("Send button not found")

        except Exception as e:
            print(f"Error sending connection request: {e}")
            return False

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




