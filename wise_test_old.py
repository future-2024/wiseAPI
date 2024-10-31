# first of all, before looking this project please send me your contact app information so we can continue to do it smoothly.

import requests
import logging
# import sys
import uuid
from dotenv import load_dotenv
import os
load_dotenv()

# Configuration of log file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('wise_transfer.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# Get Data from .env file
API_URL_V1 = os.getenv("API_URL_V1")
API_URL_V2 = os.getenv("API_URL_V2")
API_URL_V3 = os.getenv("API_URL_V3")

API_TOKEN = os.getenv("API_TOKEN")
RECIPIENT_IBAN = os.getenv("RECIPIENT_IBAN")
RECIPIENT_NAME = os.getenv("RECIPIENT_NAME")
REFERENCE = os.getenv("REFERENCE")

# Get recipent address from .env file 
CITY = os.getenv("CITY")
COUNTRYCODE = os.getenv("COUNTRYCODE")
POSTALCODE = os.getenv("POSTALCODE")
STATE = os.getenv("STATE")
FIRSTLINE = os.getenv("FIRSTLINE")

# Hearder define
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}
headers2 = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
    'X-idempotence-uuid': str(uuid.uuid4())
}

def get_profiles():
    url = f'{API_URL_V1}/profiles'
    print("------------ Getting profile start ------------")
    logging.debug(f'Fetching profiles from {url}')
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    profiles = response.json()
    logging.debug(f'Profiles retrieved: {profiles}')
    print("------------ Getting profile end ------------")
    return profiles

def get_borderless_accounts(profile_id):
    print("------------ Get borderlesss accounts start ------------")
    url = f'{API_URL_V1}/borderless-accounts?profileId={profile_id}'
    logging.debug(f'Fetching borderless accounts from {url}')
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    accounts = response.json()
    logging.debug(f'Borderless accounts retrieved: {accounts}')    
    print("------------ Get borderlesss accounts end ------------")
    return accounts

def create_conversion_quote(profile_id, source_currency, target_currency, amount, pay_out):    
    print("------------ Create conversion quote start ------------")
    url = f'{API_URL_V1}/quotes'
    data = {
        'profile': profile_id,
        'source': source_currency,
        'target': target_currency,
        'sourceAmount': amount,
        'rateType': 'FIXED',
        'type': 'BALANCE_CONVERSION',
        'payOut': pay_out
    }
    logging.debug(f'Creating conversion quote with data: {data}')
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    quote = response.json()
    logging.debug(f'Conversion quote created: {quote}')
    print("------------ Create conversion quote end ------------")
    return quote

def perform_balance_conversion(profile_id, quote_id):
    print("------------ Perform balance conversion start ------------")    
    url = f'{API_URL_V2}/profiles/{profile_id}/balance-movements'
    data = {
        'quoteId': quote_id
    }
    logging.debug(f'Performing balance conversion with data: {data}')
    response = requests.post(url, headers=headers2, json=data)
    response.raise_for_status()
    conversion = response.json()    
    print("------------ Perform balance conversion end ------------")   
    logging.info(f'Balance conversion completed: {conversion}')
    return conversion

def create_transfer_quote(profile_id, source_currency, target_currency, amount):
    print("------------ Create transfer quote start ------------") 
    url = f'{API_URL_V2}/quotes'
    data = {
        'profile': profile_id,
        'sourceCurrency': source_currency,
        'targetCurrency': target_currency,
        'sourceAmount': amount,
        'rateType': 'FIXED'
    }
    logging.debug(f'Creating transfer quote with data: {data}')
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    quote = response.json()
    logging.debug(f'Transfer quote created: {quote}')
    print("------------ Create transfer quote end ------------") 
    return quote

def create_recipient_account(profile_id):    
    print("------------ Create recipient account start ------------") 
    url = f'{API_URL_V1}/accounts'
    data = {
        'profile': profile_id,
        'accountHolderName': RECIPIENT_NAME,
        'currency': 'GBP',
        'type': 'iban',
        'details': {
            'iban': RECIPIENT_IBAN,
            "address": {
                "city": CITY,
                "countryCode": COUNTRYCODE,
                "postCode": POSTALCODE,
                "state": STATE,
                "firstLine": FIRSTLINE
            },
        }
    }
    logging.debug(f'Creating recipient account with data: {data}')
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    account = response.json()
    logging.info(f'Recipient account created: {account}')
    print("------------ Create recipient account end ------------") 
    return account['id']

def create_transfer(profile_id, target_account_id, quote_id, reference):    
    print("------------ Create transfer start ------------") 
    url = f'{API_URL_V1}/transfers'
    data = {
        'targetAccount': target_account_id,
        'quoteUuid': quote_id,
        'customerTransactionId': str(uuid.uuid4()),
        'details': {
            'reference': reference,
        }
    }
    logging.debug(f'Creating transfer with data: {data}')
    response = requests.post(url, headers=headers, json=data)
    
    response.raise_for_status()
    transfer = response.json()    
    print("------------ Create transfer end ------------") 
    logging.info(f'Transfer created with ID: {transfer["id"]}')
    logging.debug(f'Transfer details: {transfer}')
    return transfer

def fund_transfer(profile_id, transfer_id):    
    print("------------ Fund transfer start ------------") 
    url = f'{API_URL_V3}/profiles/23582544/transfers/{transfer_id}/payments'
    data = {
        'type': 'BALANCE'
    }
    logging.debug(f'Funding transfer {transfer_id} with data: {data}')
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    payment = response.json()
    logging.info(f'Transfer funded: {payment}')
    print("------------ Fund transfer end ------------")
    print("Payment completed!") 
    return payment

def main():
    try:
        profiles = get_profiles()
        if not profiles:
            logging.error('No profiles found.')
            return
        profile_id = profiles[0]['id']
        logging.info(f'Using profile ID: {profile_id}')

        accounts = get_borderless_accounts(profile_id)
        if not accounts:
            logging.error('No borderless accounts found.')
            return
        logging.info(f'Using account ID: {accounts}')
        
        borderless_account_id = accounts[0]['id']
        logging.info(f'Using borderless account ID: {borderless_account_id}')

        balances = accounts[0]['balances']
        logging.debug(f'Balances: {balances}')

        eur_balance = next((b for b in balances if b['currency'] == 'EUR'), None)
        if not eur_balance:
            logging.error('No EUR balance found.')
            return

        available_amount = float(eur_balance['amount']['value'])
        logging.info(f'EUR Balance: {available_amount}')
        
        if available_amount <= 0:
            logging.info('No positive EUR balance to convert.')
            return
        
        conversion_quote = create_conversion_quote(profile_id, 'EUR', 'USD', available_amount, 'BALANCE_PAYOUT')
        quote_id = conversion_quote['id']

        logging.info(f'Created quote ID for balance conversion: {quote_id}')
        conversion = perform_balance_conversion(profile_id, quote_id)
        logging.info(f'Balance conversion completed: {conversion}')

        accounts = get_borderless_accounts(profile_id)
        balances = accounts[0]['balances']

        usd_balance = next((b for b in balances if b['currency'] == 'USD'), None)
        if not usd_balance:
            logging.error('No USD balance found.')
            return

        usd_amount = float(usd_balance['amount']['value'])
        logging.info(f'USD Balance: {usd_amount}')

        if usd_amount <= 0:
            logging.info('No positive USD balance to transfer.')
            return

        transfer_quote = create_transfer_quote(profile_id, 'USD', 'GBP', usd_amount)
        transfer_quote_id = transfer_quote['id']
        logging.info(f'Created transfer quote ID: {transfer_quote_id}')

        recipient_account_id = create_recipient_account(profile_id)

        transfer = create_transfer(profile_id, recipient_account_id, transfer_quote_id, REFERENCE)
        transfer_id = transfer['id']
        logging.info(f'Transfer to recipient created with ID: {transfer_id}')

        payment = fund_transfer(profile_id, transfer_id)
        logging.info(f'Transfer funded: {payment}')

    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP error occurred: {e.response.status_code} - {e.response.text}')
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')

if __name__ == '__main__':
    main()
