import asyncio


async def get_account_balances(page, target_currency: str) -> list[dict]:
    """
    Scrapes account numbers, balances, currencies, and platform type (MT4/MT5).

    Args:
        page: Playwright Page object
        target_currency (str): e.g. 'GBP', 'USD'

    Returns:
        List of dicts:
        [
            {
                'account_number': 123456789,
                'value': 0.00,
                'currency': 'GBP',
                'platform': 'MT5'
            },
            ...
        ]
    """
    await asyncio.sleep(4)
    await page.goto("https://secure.vantagemarkets.com/accountManagement")
    await page.wait_for_selector('.el-card__body')

    account_cards = await page.query_selector_all('.el-card__body')
    results = []

    for card in account_cards:
        content = await card.inner_text()

        # only consider cards that mention our target currency
        if target_currency not in content:
            continue

        try:
            # 1) extract balance line before the currency label
            value_text = (
                content
                .split(target_currency)[0]
                .strip()
                .split("\n")[-1]
                .strip()
            )
            value = float(value_text.replace(",", "").replace("–", "0"))

            # 2) extract platform (MT4/MT5)
            platform_el = await card.query_selector('.platform_tag')
            if not platform_el:
                continue
            platform = (await platform_el.inner_text()).strip()

            # 3) extract account number (the next sibling of .platform_tag)
            account_number_handle = await platform_el.evaluate_handle(
                'el => el.nextElementSibling'
            )
            account_number_text = await account_number_handle.inner_text()
            account_number = int(account_number_text.strip())

            # 4) extract currency label from the card itself, if present
            currency_el = await card.query_selector('.center_currency')
            currency = (await currency_el.inner_text()).strip() if currency_el else target_currency

            # 5) append to results
            results.append({
                "account_number": account_number,
                "value": value,
                "currency": currency,
                "platform": platform
            })

        except Exception as e:
            print(f"Skipping a card due to error: {e}")

    return results
