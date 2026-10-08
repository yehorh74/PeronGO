import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class TimetableManager:
    BASE_URL = "https://perongo-backend.onrender.com"
    CLIENT_SIGNATURE = os.getenv("CLIENT_SIGNATURE")

    @staticmethod
    async def get_timetable(
        station_name: str,
        station_id: str | int,
        date_str: str = None,
        time_str: str = None,
        is_arrival: bool = False,
        is_web: bool = False,
        auth_token: str = None,
    ) -> tuple[list[dict], str | None]:

        endpoint = f"{TimetableManager.BASE_URL}/api/v1/schedules"

        params = {
            "stations": str(station_id),
            "is_arrival": str(is_arrival).lower(),
        }

        if date_str:
            params["date"] = date_str

        if time_str:
            params["time"] = time_str

        headers = {
            "X-App-Client": TimetableManager.CLIENT_SIGNATURE
        }

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(endpoint, params=params, headers=headers)

            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) == 0:
                    return [], f"Brak połączeń dla stacji '{station_id}'."
                return data, None
            else:
                return [], f"Błąd serwera HTTP {res.status_code}: {res.text}"

        except httpx.ConnectError:
            return [], f"Błąd połączenia: Nie można połączyć się z {TimetableManager.BASE_URL}."
        except httpx.TimeoutException:
            return [], "Błąd przekroczenia czasu (Timeout). Serwer się wybudza, spróbuj ponownie za chwilę."
        except Exception as e:
            return [], f"Niewyłapany błąd: {type(e).__name__} - {str(e)}"