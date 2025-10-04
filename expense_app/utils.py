# expense_app/utils.py - CLEAN CODE (No citation tags)
import requests
from decimal import Decimal 

# API endpoints from problem statement
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}"
COUNTRIES_API = "https://restcountries.com/v3.1/all?fields=name,currencies"

def get_exchange_rate(base_currency, target_currency):
    """Fetches the exchange rate between two currencies using the external API."""
    url = EXCHANGE_RATE_API.format(BASE_CURRENCY=base_currency)
    
    try:
        response = requests.get(url, timeout=5) 
        response.raise_for_status()
        data = response.json()
        
        rate = data.get('rates', {}).get(target_currency)
        
        if rate:
            return rate
        else:
            print(f"Error: Target currency {target_currency} not found in rates.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def convert_currency(amount, base_currency, target_currency):
    """
    Converts a Decimal amount from base currency to target currency.
    """
    if base_currency == target_currency:
        return round(amount, 2)
        
    rate = get_exchange_rate(base_currency, target_currency)
    
    if rate is not None:
        # CRITICAL FIX: Convert the float rate from the API into a Decimal object 
        rate_decimal = Decimal(str(rate)) 
        
        converted_amount = amount * rate_decimal 
        
        return round(converted_amount, 2)
    
    return None

def get_country_currencies():
    """Fetches country names and their currencies using the external API."""
    try:
        response = requests.get(COUNTRIES_API, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching country data: {e}")
        return []
        
def mock_ocr_extract(receipt_image_file):
    """
    Simulates OCR extraction of key expense fields from a receipt image.
    """
    return {
        "amount_claimed": 85.99,
        "currency_claimed": "USD",
        "category": "Meals",
        "description": "Lunch at local diner.",
        "date": "2025-10-03",
        "expense_lines": ["Burger: 15.00", "Coffee: 5.00"],
        "vendor_name": "Local Diner Co."
    }