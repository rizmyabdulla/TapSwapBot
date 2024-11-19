import os
import random
import asyncio
import glob
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright
from better_proxy import Proxy
from bot.config import settings


def get_session_names() -> list[str]:
    """Get all session names from the 'sessions' directory."""
    return [os.path.splitext(os.path.basename(file))[0] for file in glob.glob("sessions/*.session")]


def escape_html(text: str) -> str:
    """Escape HTML characters in a string."""
    text = str(text)
    return text.replace('<', '\\<').replace('>', '\\>')


def get_proxies() -> list[Proxy]:
    """Retrieve proxy configurations."""
    if settings.USE_PROXY_FROM_FILE:
        with open(file="bot/config/proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies



async def extract_chq(chq: str) -> tuple[int, str]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (Linux; Android 13; RMX3630 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36"
        )
        page = await context.new_page()

        await page.evaluate("""
            window.ctx = {};
            window.ctx.api = {};
            window.ctx.d_headers = new Map();
            window.ctx.api.setHeaders = function(entries) { for (const [W, U] of Object.entries(entries)) window.ctx.d_headers.set(W, U) }
            var chrStub = document.createElement("div");
            chrStub.id = "_chr_";
            document.body.appendChild(chrStub);
        """)

        bytes_array = bytearray(len(chq) // 2)
        xor_key = 157
        for i in range(0, len(chq), 2):
            bytes_array[i // 2] = int(chq[i:i + 2], 16)
        xor_bytes = bytearray(t ^ xor_key for t in bytes_array)
        decoded_xor = xor_bytes.decode("utf-8")

        chr_key = 10621

        chr_key += await page.evaluate("(code) => eval(code)", decoded_xor)
        cache_id = await page.evaluate("window.ctx.d_headers.get('Cache-Id')")


        await browser.close()

    return chr_key, cache_id

# if __name__ == '__main__':
    
#     chq = "fbe8f3fee9f4f2f3bdf9b5b4e6ebfcefbdd6a0c6baf0d7fcacf3f9dac5f2f5e7ece7faf3d0dccabab1baf0e9daa8f2f9f8cae7d3ebf4eff5d5abbab1baf3e9e8afead6ace5d8f5e7d2bab1baf0c7f4c4f3d7ebc4dcf8f7fbe8d3f0bab1baf0e9f7d3efe8d9f1e8faecbab1baf0c7f0acf0f9f0a9f2eac5edd8d0f3dcecdabab1baf0c7f0aff0c7e4a9e8afc5cfdcaed9efbab1baf0c7f8acefadc5abebebfbccbab1baf0d7f4a9f0d7f8c5f0e9fff8eefbefa9e7e5d6bab1bae4aeefa9bab1bae4e5ffcdbab1badeafebadeefaebd5e7faebc4decabab1baebfaebcee7ead9c4e4eaadbab1bad9e5f3d1dedabab1badcfaebd5e7faebc4decabab1bad8feacd7d9dabab1baedfaefcdd9d7a9a5e7fad1aff4fad1d6edeef7dbeae5d9dbf0fef4dae5aee4a4f4d7e4c7f0f9ecadf4d7a9a5e7fad1aff4fad1d6edeef7dbece8d9dbf0eef4dae5aee4a4f4d7e8c7f0d7f0aef4d7a9a5e7fad1aff4fad1d6edeef7dbeff8f7dbf0d4f4dae5aee4a4f4d7e4c7f3e9f8aef4d7a9a5e7fad1aff4fad1d6edeef7dbecd6fbdbf0c4f4dae5aee4a4f4d7f0aff2f9f4c4f4d7a9a5e7fad1aff4fad1d6edeef7dbe7d3cddbf3fef4dae5aee4a4f4d7daacf2f9dea9f4d7a9a5f1afefcdd9d7a9a5f1afefcdd9d7a9a5f1afefcdd9d7a9a5f1afefcdd9d7a9a5f1afefcdd9d7a9a5f1afefcdd9d7a9bab1bae7afebadefeac5d1dfeaebc8d9f8f7a8eeeaecbab1bae7afebadece5efadded0d1d4d9e5efd1bab1bae5aff3d2ded1a5bab1baebafebd4ece5ffcabab1badceaa8cdd9f8efd5d9fafbebdfd3f3d5e7d0e8bab1badceaecbab1baf0e9f8caf0c7f0aef0e5f7c8e7eac5c9d9fcbac0a6f9a0fbe8f3fee9f4f2f3b5b4e6eff8e9e8eff3bdd6a6e0a6eff8e9e8eff3bdf9b5b4a6e0fbe8f3fee9f4f2f3bdf8b5fcb1ffb4e6ebfcefbdfea0f9b5b4a6eff8e9e8eff3bdf8a0fbe8f3fee9f4f2f3b5fbb1fab4e6fba0fbb0ade5acaaaea6ebfcefbdf5a0fec6fbc0a6f4fbb5f8c6baedf3eec4f3c9bac0a0a0a0e8f3f9f8fbf4f3f8f9b4e6ebfcefbdf4a0fbe8f3fee9f4f2f3b5f0b4e6ebfcefbdf3a0bafcfffef9f8fbfaf5f4f7f6f1f0f3f2edecefeee9e8ebeae5e4e7dcdfded9d8dbdad5d4d7d6d1d0d3d2cdcccfcec9c8cbcac5c4c7adacafaea9a8abaaa5a4b6b2a0baa6ebfcefbdf2a0babab1eda0babab1eca0f2b6f4a6fbf2efb5ebfcefbdefa0ade5adb1eeb1e9b1e8a0ade5ada6e9a0f0c6bafef5fcefdce9bac0b5e8b6b6b4a6e3e9bbbbb5eea0efb8ade5a9a2eeb7ade5a9adb6e9a7e9b1efb6b6b8ade5a9b4a2f2b6a0ecc6bafef5fcefdef2f9f8dce9bac0b5e8b6ade5fcb4b0ade5fcbca0a0ade5ada2cee9eff4f3fac6bafbeff2f0def5fcefdef2f9f8bac0b5ade5fbfbbbeea3a3b5b0ade5afb7efbbade5abb4b4a7efa7ade5adb4e6e9a0f3c6baf4f3f9f8e5d2fbbac0b5e9b4a6e0fbf2efb5ebfcefbdeba0ade5adb1eaa0f2c6baf1f8f3fae9f5bac0a6eba1eaa6ebb6b6b4e6edb6a0bab8bab6b5baadadbab6f2c6bafef5fcefdef2f9f8dce9bac0b5ebb4c6bae9f2cee9eff4f3fabac0b5ade5acadb4b4c6baeef1f4fef8bac0b5b0ade5afb4a6e0eff8e9e8eff3bdf9f8fef2f9f8c8cfd4def2f0edf2f3f8f3e9b5edb4a6e0a6f8c6bae8e4e9d6e8e7bac0a0f4b1fca0fceffae8f0f8f3e9eeb1f8c6baedf3eec4f3c9bac0a0bcbcc6c0a6e0ebfcefbdf7a0fec6ade5adc0b1f6a0fbb6f7b1f1a0fcc6f6c0a6f4fbb5bcf1b4e6ebfcefbdf0a0fbe8f3fee9f4f2f3b5f3b4e6e9f5f4eec6badfffd0f9cdf1bac0a0f3b1e9f5f4eec6bad9f9e8e9d6d5bac0a0c6ade5acb1ade5adb1ade5adc0b1e9f5f4eec6baf0ccf3f3d6e9bac0a0fbe8f3fee9f4f2f3b5b4e6eff8e9e8eff3baf3f8eacee9fce9f8baa6e0b1e9f5f4eec6bac7d9f3f3f9e5bac0a0bac1e5a8feeab6c1e5afadb7c1e5a8feb5c1e5a8feb4c1e5afadb7e6c1e5a8feeab6c1e5afadb7bab1e9f5f4eec6baefc7f9d4c5d8bac0a0bac6c1e5afaae1c1e5afafc0b3b6c6c1e5afaae1c1e5afafc0a6a2c1e5afadb7e0baa6e0a6f0c6baedeff2e9f2e9e4edf8bac0c6bac5fae5e7ffeebac0a0fbe8f3fee9f4f2f3b5b4e6ebfcefbdf3a0f3f8eabdcff8fad8e5edb5e9f5f4eec6bac7d9f3f3f9e5bac0b6e9f5f4eec6baefc7f9d4c5d8bac0b4b1f2a0f3c6bae9f8eee9bac0b5e9f5f4eec6baf0ccf3f3d6e9bac0c6bae9f2cee9eff4f3fabac0b5b4b4a2b0b0e9f5f4eec6bad9f9e8e9d6d5bac0c6ade5acc0a7b0b0e9f5f4eec6bad9f9e8e9d6d5bac0c6ade5adc0a6eff8e9e8eff3bde9f5f4eec6bad6c4caccf4dbbac0b5f2b4a6e0b1f0c6baedeff2e9f2e9e4edf8bac0c6bad6c4caccf4dbbac0a0fbe8f3fee9f4f2f3b5f3b4e6f4fbb5bcdff2f2f1f8fcf3b5e3f3b4b4eff8e9e8eff3bdf3a6eff8e9e8eff3bde9f5f4eec6bafbf1f4ffedcbbac0b5e9f5f4eec6badfffd0f9cdf1bac0b4a6e0b1f0c6baedeff2e9f2e9e4edf8bac0c6bafbf1f4ffedcbbac0a0fbe8f3fee9f4f2f3b5f3b4e6fbf2efb5ebfcefbdf2a0ade5adb1eda0e9f5f4eec6bad9f9e8e9d6d5bac0c6baf1f8f3fae9f5bac0a6f2a1eda6f2b6b6b4e6e9f5f4eec6bad9f9e8e9d6d5bac0c6baede8eef5bac0b5d0fce9f5c6baeff2e8f3f9bac0b5d0fce9f5c6baeffcf3f9f2f0bac0b5b4b4b4b1eda0e9f5f4eec6bad9f9e8e9d6d5bac0c6baf1f8f3fae9f5bac0a6e0eff8e9e8eff3bdf3b5e9f5f4eec6bad9f9e8e9d6d5bac0c6ade5adc0b4a6e0b1f3f8eabdf0b5f8b4c6bac5fae5e7ffeebac0b5b4b1f5a0f8c6bae8e4e9d6e8e7bac0b5f5b4b1fcc6f6c0a0f5a6e0f8f1eef8bdf5a0f1a6eff8e9e8eff3bdf5a6e0b1f8b5fcb1ffb4a6e0b5fbe8f3fee9f4f2f3b5fcb1ffb4e6ebfcefbdd4a0f8b1fea0fcb5b4a6eaf5f4f1f8b5bcbcc6c0b4e6e9efe4e6ebfcefbdfba0b0edfcefeef8d4f3e9b5d4b5ade5acaaaeb4b4b2ade5acb6edfcefeef8d4f3e9b5d4b5ade5acaaa9b4b4b2ade5afb6edfcefeef8d4f3e9b5d4b5ade5acaaa8b4b4b2ade5aeb6b0edfcefeef8d4f3e9b5d4b5ade5acaaabb4b4b2ade5a9b7b5edfcefeef8d4f3e9b5d4b5ade5acaaaab4b4b2ade5a8b4b6edfcefeef8d4f3e9b5d4b5ade5acaaa5b4b4b2ade5abb7b5edfcefeef8d4f3e9b5d4b5ade5acaaa4b4b4b2ade5aab4b6b0edfcefeef8d4f3e9b5d4b5ade5acaafcb4b4b2ade5a5b7b5edfcefeef8d4f3e9b5d4b5ade5acaaffb4b4b2ade5a4b4b6edfcefeef8d4f3e9b5d4b5ade5acaafeb4b4b2ade5fca6f4fbb5fba0a0a0ffb4ffeff8fcf6a6f8f1eef8bdfec6baede8eef5bac0b5fec6baeef5f4fbe9bac0b5b4b4a6e0fefce9fef5b5fab4e6fec6baede8eef5bac0b5fec6baeef5f4fbe9bac0b5b4b4a6e0e0e0b5f9b1ade5f9acaafbadb4b1b5fbe8f3fee9f4f2f3b5b4e6ebfcefbdd7a0f8b1f5a0e6baeacae4d4cfbaa7bab5b5b5b3b6b4b6b4b6b4b6b9bab1bafcd3fecbdfbaa7fbe8f3fee9f4f2f3b5d9b4e6eff8e9e8eff3bdd9b5b4a6e0b1badbdedcc9f7baa7d7b5ade5acaaf9b4b1bad3e9dbfeebbaa7d7b5ade5acaaf8b4b1bacde4d9d5f5baa7d7b5ade5acaafbb4b1bacec4e7e4e4baa7baeaf4f3f9f2eabab1bafcfaeef4d9baa7d7b5ade5aca5adb4b1bae7fed3effbbaa7d7b5ade5aca5acb4b1baccdff8d7d6baa7d7b5ade5aca5afb4b1bae9dec8fff0baa7d7b5ade5aca5aeb4b1badacdcacbf2baa7d7b5ade5aca5a9b4b1bad9d8cbceedbaa7bac2dcdac2acbab1bacdf5f0c8e5baa7fbe8f3fee9f4f2f3b5d9b1d8b4e6eff8e9e8eff3bdd9b8d8a6e0b1baf4d3d6d6e7baa7fbe8f3fee9f4f2f3b5d9b1d8b4e6eff8e9e8eff3bdd9b6d8a6e0b1baccebe8e9e7baa7fbe8f3fee9f4f2f3b5d9b1d8b4e6eff8e9e8eff3bdd9b5d8b4a6e0e0b1f4a0b5fbe8f3fee9f4f2f3b5b4e6ebfcefbdd9a0bcbcc6c0a6eff8e9e8eff3bdfbe8f3fee9f4f2f3b5d8b1dbb4e6ebfcefbddaa0d9a2fbe8f3fee9f4f2f3b5b4e6f4fbb5dbb4e6ebfcefbdd5a0dbc6bafcededf1e4bac0b5d8b1fceffae8f0f8f3e9eeb4a6eff8e9e8eff3bddba0f3e8f1f1b1d5a6e0e0a7fbe8f3fee9f4f2f3b5b4e6e0a6eff8e9e8eff3bdd9a0bcc6c0b1daa6e0a6e0b5b4b4b1f7a0f4b5e9f5f4eeb1fbe8f3fee9f4f2f3b5b4e6eff8e9e8eff3bdf7c6bae9f2cee9eff4f3fabac0b5b4c6baeef8fceffef5bac0b5f5c6baeacae4d4cfbac0b4c6bae9f2cee9eff4f3fabac0b5b4c6bafef2f3eee9efe8fee9f2efbac0b5f7b4c6baeef8fceffef5bac0b5f5c6baeacae4d4cfbac0b4a6e0b4a6f5c6bafcd3fecbdfbac0b5f7b4a6e9efe4e6f8ebfcf1b5baf9f2fee8f0f8f3e9c6c1bafaf8e9d8f1f8f0f8f3e9dfe4d4f9c1bac0a6bab4a6e0fefce9fef5e6eff8e9e8eff3bdade5feadfbf8fffcfff8a6e0ebfcefbdf6a0f5c6badbdedcc9f7bac0b1f1a0f5c6bad3e9dbfeebbac0b1f0a0f5c6bacde4d9d5f5bac0b1f3a0badefcfef5f8b0d4f9baa6e9efe4e6ebfcefbdf2a0e6e0a6f2c6f3c0a0baeba8f1ffe9defca5bab1eaf4f3f9f2eac6f6c0c6f1c0c6f0c0b5f2b4a6e0fefce9fef5e6e0ebfcefbdeda0f9f2fee8f0f8f3e9b1eca0d7b5ade5aca5a8b4b1efa0d7b5ade5aca5abb4b1eea0edc6ecc0b5d7b5ade5aca5aab4b4b1e9a0f5c6bacec4e7e4e4bac0b1e4a0f8ebfcf1b5e9b4c6f5c6bafcfaeef4d9bac0c0a2b3c6d7b5ade5aca5a5b4c0a2b3c6d7b5ade5aca5a4b4c0a2b3c6f5c6bae7fed3effbbac0c0a2b3c6d7b5ade5aca5fcb4c0e1e1ade5adb1e7a0f8ebfcf1b5e9b4c6f5c6badbdedcc9f7bac0c0a2b3c6f5c6bad3e9dbfeebbac0c0a2b3c6f5c6baccdff8d7d6bac0c0a2b3c6bafaf8e9bac0b5f5c6bae9dec8fff0bac0b4e1e1baadbaa6eec6baf4f3f3f8efd5c9d0d1bac0a0f5c6badacdcacbf2bac0a6ebfcefbddca0edc6ecc0b5f5c6bad9d8cbceedbac0b4c6efc0b5bac2ebbab4b1dfa0edc6ecc0b5bac2d9dfc2afbab4c6efc0b5bac2ebbab4b1dea0b6dca6eff8e9e8eff3bddeb7a0deb1deb7a0b6dfb1deb8a0ade5f8feaaada4b1deb6a0f5c6bacdf5f0c8e5bac0b5e4b1f5c6baf4d3d6d6e7bac0b5ade5afaaacadb1f5c6baccebe8e9e7bac0b5d3e8f0fff8efb1e7b4b4b4b1dea6e0b5b4b4b4a6"
#     print(asyncio.run(extract_chq(chq))) #10,621


# @asynccontextmanager
# async def create_webdriver():
#     """Create an async Playwright context with mobile emulation."""
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context(
#             viewport={"width": 375, "height": 812},
#             user_agent="Mozilla/5.0 (Linux; Android 13; RMX3630 Build/TP1A.220905.001; wv) "
#                        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36"
#         )
#         page = await context.new_page()
#         try:
#             yield page
#         finally:
#             await browser.close()


# async def login_in_browser(auth_url: str, proxy: str = None) -> tuple[str, str, str]:
#     """Log in through the browser and extract required tokens."""
#     async with create_webdriver() as page:
#         if proxy:
#             async def route_handler(route):
#                 await route.continue_(headers={"Proxy": proxy})

#             await page.context.route("**/*", route_handler)

#         await page.goto(auth_url)
#         await asyncio.sleep(random.randint(7, 15))

#         # Try to click 'Skip' button if available
#         try:
#             await page.locator('xpath=//*[@id="app"]/div[2]/button').click()
#             await asyncio.sleep(random.randint(2, 5))
#         except:
#             print('Skip button not found')

#         # Try to click on 'coin' button if available
#         try:
#             await page.locator('xpath=//*[@id="ex1-layer"]').click()
#         except:
#             print('Coin button not found')

#         await asyncio.sleep(5)

#         response_text = '{}'
#         x_cv = '651'
#         x_touch = '1'

#         # Intercept and process requests
#         for request in await page.context.storage_state():
#             if request.url == "https://api.tapswap.club/api/account/challenge" and 'chr' in request.post_data:
#                 response_text = request.response.body

#             if request.url == "https://api.tapswap.club/api/player/submit_taps":
#                 headers = request.headers
#                 x_cv = headers.get('x-cv') or headers.get('X-Cv', '')
#                 x_touch = headers.get('x-touch') or headers.get('X-Touch', '')
#     print(response_text, x_cv, x_touch)

#     return response_text, x_cv, x_touch