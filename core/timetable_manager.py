import os
import httpx

def load_env_safely():
    if "CLIENT_SIGNATURE" in os.environ:
        return

    env_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
    ]

    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            os.environ[key.strip()] = val.strip().strip('"').strip("'")
                break
            except Exception:
                pass

load_env_safely()

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