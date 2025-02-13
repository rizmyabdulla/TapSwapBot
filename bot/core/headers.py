from bot.config import settings

headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://app.tapswap.club',
    'Referer': 'https://app.tapswap.club/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; RMX3630 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36',
    'Sec-Ch-Ua': '"Android WebView";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'X-App': 'tapswap_server',
    'Cache-Id': '',
    'X-Cv': str(settings.X_CV_KEY),
    'X-Touch': str(settings.X_TOUCH_KEY),
}
