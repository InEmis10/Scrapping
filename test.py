import json
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / ".cache" / "browser_profile"
COOKIES_FILE = BASE_DIR / ".cache" / "cookies.json"
API = "https://my.epitech.eu/api"


def fetch_token(headless: bool = False) -> str:
    token = None

    def on_request(request):
        nonlocal token
        auth = request.headers.get("authorization", "")
        if request.url.startswith(API) and auth.startswith("Bearer "):
            token = auth.removeprefix("Bearer ")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=headless,
            args=["--ozone-platform=x11"],
        )

        # Restaure les cookies sauvegardés (y compris les cookies de session)
        if COOKIES_FILE.exists():
            context.add_cookies(json.loads(COOKIES_FILE.read_text()))

        page = context.pages[0] if context.pages else context.new_page()
        page.on("request", on_request)
        page.goto("https://my.epitech.eu/dashboard")

        for _ in range(240):  # 2 min max pour te connecter
            if token:
                break
            page.wait_for_timeout(500)

        # Sauvegarde tous les cookies avant de fermer
        COOKIES_FILE.write_text(json.dumps(context.cookies(), indent=2))
        context.close()

    if token is None:
        raise RuntimeError("Jeton non récupéré : connexion non terminée ?")
    return token


if __name__ == "__main__":
    token = fetch_token()
    res = requests.get(
        f"{API}/students/profile",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    print("[STATUS]:", res.status_code)
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))