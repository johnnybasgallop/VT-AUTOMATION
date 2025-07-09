import asyncio
import asyncio.selector_events
import os
import time
from pprint import pprint

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from utilities.accounts import get_account_balances
from utilities.login import login
from utilities.transfer_calculation import calculate_transfers

load_dotenv()

async def run():
    async with async_playwright() as p:

        # Browser init
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        page = await context.new_page()

        # User login
        await login(page, os.getenv("EXAMPLE_EMAIL"), os.getenv("EXAMPLE_PASSWORD"))


        # Read balance into array
        gbp_balances = await get_account_balances(page, "GBP")
        usd_balances = await get_account_balances(page, "USD")

        print(f"gbp: {gbp_balances}")
        print(f"usd: {usd_balances}")

        result = calculate_transfers(gbp_balances, min_balance=200, currency='GBP')
        pprint(result)

        await asyncio.sleep(180)

        await browser.close()

asyncio.run(run())
