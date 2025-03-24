"""
Account Generation Module for Redeye

Handles bulk account creation for various stores.
"""

import os
import json
import random
import string
import aiohttp
import logging
import asyncio
from typing import List, Dict, Tuple
import names  # for generating random names
import io
import discord

logger = logging.getLogger('discord_bot.modules.redeye.account_gen')

def generate_random_string(length: int) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_password() -> str:
    """Generate a password that meets Luisaviaroma requirements."""
    # At least one uppercase, one lowercase, one number, one special char
    # Length between 8-12 characters
    special_chars = "!@#$%^&*"
    password = [
        random.choice(string.ascii_uppercase),  # one uppercase
        random.choice(string.ascii_lowercase),  # one lowercase
        random.choice(string.digits),           # one number
        random.choice(special_chars),           # one special char
    ]
    
    # Add random chars to reach a length between 8-12
    length = random.randint(8, 12)
    remaining_length = length - len(password)
    all_chars = string.ascii_letters + string.digits + special_chars
    password.extend(random.choices(all_chars, k=remaining_length))
    
    # Shuffle the password
    random.shuffle(password)
    return ''.join(password)

async def get_proxy() -> str:
    """Get a proxy from the proxy service."""
    try:
        proxy_url = os.getenv('PROXY_SERVICE_URL')
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy_url) as response:
                if response.status == 200:
                    proxies = await response.text()
                    proxy_list = [p.strip() for p in proxies.split() if p.strip()]
                    if proxy_list:
                        return random.choice(proxy_list)
    except Exception as e:
        logger.error(f"Error fetching proxy: {e}")
    return None

async def generate_lvr_account(catchall: str, proxy: str = None) -> Tuple[str, str]:
    """Generate a single Luisaviaroma account."""
    try:
        # Generate random credentials
        email = f"{generate_random_string(10)}{catchall}"
        password = generate_password()
        first_name = names.get_first_name()
        last_name = names.get_last_name()

        # Prepare request data
        data = {
            "Privacy": True,
            "Newsletter": True,
            "Loyalty": True,
            "ProfilingAgree": True,
            "FirstName": first_name,
            "LastName": last_name,
            "UserId": email,
            "Password": password,
            "RePassword": password,
            "SmsAgree": False,
            "Language": "IT",
            "Channel": "account"
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'it-IT,it;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.luisaviaroma.com',
            'referer': 'https://www.luisaviaroma.com/myarea/login',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'Host': 'www.luisaviaroma.com'
        }

        # Setup proxy if provided
        proxy_url = f"http://{proxy}" if proxy else None
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://www.luisaviaroma.com/myarea/usersession/registeruser',
                json=data,
                headers=headers,
                proxy=proxy_url,
                timeout=30
            ) as response:
                if response.status == 200:
                    return email, password
                else:
                    logger.error(f"Account creation failed with status {response.status}")
                    return None, None

    except Exception as e:
        logger.error(f"Error generating account: {e}")
        return None, None

async def generate_accounts(storename: str, catchall: str, quantity: int) -> List[Tuple[str, str]]:
    """Generate multiple accounts for the specified store."""
    if storename.lower() != "luisaviaroma":
        return []

    successful_accounts = []
    tasks = []

    # Create a pool of proxies
    proxy_pool = []
    for _ in range(min(quantity, 10)):  # Get a reasonable number of proxies
        proxy = await get_proxy()
        if proxy:
            proxy_pool.append(proxy)

    # Generate accounts with proxy rotation
    for i in range(quantity):
        proxy = random.choice(proxy_pool) if proxy_pool else None
        task = asyncio.create_task(generate_lvr_account(catchall, proxy))
        tasks.append(task)
        # Add small delay between requests
        await asyncio.sleep(0.5)

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful accounts
    for email, password in results:
        if email and password:
            successful_accounts.append((email, password))

    return successful_accounts

def create_accounts_file(accounts: List[Tuple[str, str]]) -> discord.File:
    """Create a text file containing the generated accounts."""
    content = "\n".join([f"{email}:{password}" for email, password in accounts])
    file = discord.File(
        io.StringIO(content),
        filename="accounts.txt"
    )
    return file 