import asyncio


async def login(page, email: str, password: str):
        await page.goto("https://secure.vantagemarkets.com/login")

        await asyncio.sleep(4)
        await page.click('[id="adroll_consent_accept"]')

        await asyncio.sleep(4)
        # 2. Fill in login details with typing delay
        # Click the field:
        await page.click('[data-testid="userName_login"]')
        await page.wait_for_selector('[data-testid="userName_login"]')
        await page.type('[data-testid="userName_login"]', email, delay=200)  # 100ms per character


        await page.click('[data-testid="password_login"]')
        await page.wait_for_selector('[data-testid="password_login"]')
        await page.type('[data-testid="password_login"]', password, delay=250)  # 100ms per character


        await asyncio.sleep(2)

        await page.click('[data-testid="login"]')

        await asyncio.sleep(2)
