import asyncio
import argparse
from itertools import cycle

from pyrogram import Client, compose

from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper
from bot.core.query import run_query_tapper
from bot.core.registrator import register_sessions
from bot.utils.scripts import get_session_names, get_proxies

options = """
Select an action:

    1. Run clicker (Session)
    2. Create session
    3. Run clicker (Query)
"""


global tg_clients


async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:
        print(options)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2", "3"]:
                logger.warning("Action must be 1, 2 or 3")
            else:
                action = int(action)
                break

    if action == 1:
        tg_clients = await get_tg_clients()

        await run_tasks(tg_clients=tg_clients)
    elif action == 2:
        await register_sessions()
    elif action == 3:
        with open("data.txt", "r") as f:
                query_ids = [line.strip() for line in f.readlines()]
        await run_tasks_query(query_ids)

async def run_tasks_query(query_ids: list[str]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    account_name = [i for i in range(len(query_ids) + 10)]
    name_cycle = cycle(account_name)
    lock = asyncio.Lock()
    tasks = [
        asyncio.create_task(
            run_query_tapper(
                query=query,
                proxy=next(proxies_cycle) if proxies_cycle else None,
                session_name=f"Account{next(name_cycle)}",
                lock=lock
            )
        )
        for query in query_ids
    ]

    await asyncio.gather(*tasks)

async def run_tasks(tg_clients: list[Client]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    lock = asyncio.Lock()

    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client,
                proxy=next(proxies_cycle) if proxies_cycle else None,
                lock=lock,
            )
        )
        for tg_client in tg_clients
    ]

    await asyncio.gather(*tasks)
