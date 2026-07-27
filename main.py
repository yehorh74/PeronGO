import os
from pathlib import Path
from urllib import response
import flet as ft
import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    try:
        load_dotenv()
    except Exception:
        pass

API_KEY = os.getenv("X_API_Key")
API_URL = os.getenv("PLK_API_URL", "https://pdp-api.plk-sa.pl/api/v1")

def main(page: ft.Page):
    page.title = "PeronGO – Tablica odjazdów"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    status_label = ft.Text(value="Kliknij przycisk, aby pobrać dane", size=16)

    def fetch_data(e):
        if not API_KEY:
            status_label.value = "Błąd: Brak klucza X_API_Key w pliku .env!"
            page.update()
            return

        headers = {
            "X_Api_Key": API_KEY,
            "Accept": "application/json"
        }

        try:
            response = requests.get(f"{API_URL}/stations", headers=headers, timeout=5)
            if response.status_code == 200:
                status_label.value = "Połączono z API PKP PLK pomyślnie!"
            else:
                status_label.value = f"Błąd API: {response.status_code}"
        except Exception as err:
            status_label.value = f"Błąd połączenia: {err}"
        
        page.update()

    page.add(
        ft.Text("PeronGO", size=28, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Sprawdź połączenie z API", on_click=fetch_data),
        status_label
    )

if __name__ == "__main__":
    ft.run(main)