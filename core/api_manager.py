import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

class APIManager:
    def __init__(self):
        # Ładowanie pliku .env
        env_path = Path(__file__).parent.parent / ".env" if (Path(__file__).parent.parent / ".env").exists() else Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            try:
                load_dotenv()
            except Exception:
                pass

        self.api_key = os.getenv("X_API_KEY")
        self.api_url = os.getenv("PLK_API_URL", "https://pdp-api.plk-sa.pl/api/v1")

    def _get_headers(self) -> dict:
        return {
            "X-Api-Key": self.api_key or "",
            "Accept": "application/json"
        }

    async def test_connection(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "Błąd: Brak klucza X_API_KEY w pliku .env!"

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.api_url}/stations", headers=self._get_headers())
                if response.status_code == 200:
                    return True, "Połączono z API PKP PLK pomyślnie!"
                return False, f"Błąd API: {response.status_code}"
            except Exception as err:
                return False, f"Błąd połączenia: {err}"

    async def fetch_stations(self) -> tuple[bool, list | dict | str]:
        if not self.api_key:
            return False, "Błąd: Brak klucza API"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.api_url}/stations", headers=self._get_headers())
                if response.status_code == 200:
                    return True, response.json()
                return False, f"Błąd API: {response.status_code}"
            except Exception as err:
                return False, f"Błąd sieci: {err}"