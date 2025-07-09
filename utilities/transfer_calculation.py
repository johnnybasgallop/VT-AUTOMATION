from pprint import pprint
from typing import Any, Dict, List


def calculate_transfers(
    accounts: List[Dict[str, Any]],
    min_balance: float,
    currency: str
) -> Dict[str, Any]:
    """
    Redistribute funds among the given accounts to maximize the number of accounts
    reaching at least min_balance, considering only those in the specified currency.

    Args:
        accounts: List of account dicts, each with keys
            - 'account_number': int
            - 'value': float
            - 'currency': str
        min_balance: The minimum balance required to consider an account funded.
        currency:       Only accounts with this currency will be considered.

    Returns:
        {
            'final_accounts': List of all accounts with updated balances,
            'funded_accounts': List of account_numbers now >= min_balance,
            'transfers': List of {
                'from': int,    # donor account_number
                'to': int,      # receiver account_number
                'amount': float # amount transferred
            }
        }
    """
    # Make a shallow copy so we don’t mutate the original input
    final_accounts = [acct.copy() for acct in accounts]

    # Index accounts by account_number for quick lookup
    acct_map = {acct['account_number']: acct for acct in final_accounts}

    # Filter to only the specified currency
    in_cur = [acct for acct in final_accounts if acct['currency'] == currency]

    # Separate into already funded, donors (value > min_balance), and receivers (value < min_balance)
    funded = {acct['account_number'] for acct in in_cur if acct['value'] >= min_balance}
    donors = {
        acct['account_number']: acct['value'] - min_balance
        for acct in in_cur
        if acct['value'] > min_balance
    }
    receivers = [
        acct for acct in in_cur
        if acct['value'] < min_balance
    ]

    # Sort receivers by descending current value (closest to funding)
    receivers.sort(key=lambda a: a['value'], reverse=True)

    transfers: List[Dict[str, Any]] = []

    # Total available surplus across all donors
    total_available = sum(donors.values())

    # Helper lists for finding single-donor and pooling
    # single_donors sorted by smallest surplus first
    single_donors = sorted(donors, key=lambda d: donors[d])
    # pooling donors sorted by largest surplus first
    pool_donors = sorted(donors, key=lambda d: donors[d], reverse=True)

    for recv in receivers:
        recv_id = recv['account_number']
        needed = min_balance - recv['value']

        # If we can no longer fund even the easiest receiver, stop
        if total_available < needed:
            break

        # Try single-donor fill
        donor_id = next((d for d in single_donors if donors[d] >= needed), None)
        if donor_id is not None:
            # Perform transfer
            transfers.append({'from': donor_id, 'to': recv_id, 'amount': needed})
            # Update balances
            donors[donor_id] -= needed
            acct_map[donor_id]['value']   -= needed
            acct_map[recv_id]['value']    += needed
            total_available              -= needed
        else:
            # Pool from multiple donors
            remaining = needed
            for d in pool_donors:
                avail = donors[d]
                if avail <= 0:
                    continue
                give = min(avail, remaining)
                transfers.append({'from': d, 'to': recv_id, 'amount': give})
                donors[d]                     -= give
                acct_map[d]['value']          -= give
                acct_map[recv_id]['value']    += give
                total_available              -= give
                remaining                     -= give
                if remaining <= 0:
                    break

        # Mark as funded
        funded.add(recv_id)

        # Recompute helper lists (in case we exhausted some donors)
        single_donors = [d for d in single_donors if donors[d] > 0]
        single_donors.sort(key=lambda d: donors[d])
        pool_donors   = [d for d in pool_donors   if donors[d] > 0]
        pool_donors.sort(key=lambda d: donors[d], reverse=True)

    return {
        'final_accounts': final_accounts,
        'funded_accounts': sorted(funded),
        'transfers': transfers
    }

# Example usage:
if __name__ == '__main__':
    accounts = [
        {'account_number': 1, 'value': 840, 'currency': 'GBP'},
        {'account_number': 2, 'value':   840, 'currency': 'GBP'},
        {'account_number': 3, 'value':   840, 'currency': 'GBP'},
        {'account_number': 4, 'value': 840, 'currency': 'GBP'},
        {'account_number': 5, 'value':  840, 'currency': 'GBP'},
        {'account_number': 6, 'value': 840, 'currency': 'GBP'},
        {'account_number': 7, 'value': 0, 'currency': 'GBP'},
    ]
    result = calculate_transfers(accounts, min_balance=720, currency='GBP')
    pprint(result)
