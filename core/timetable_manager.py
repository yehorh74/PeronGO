import os
import httpx
from dotenv import load_dotenv

from core.i18n import _
from core.logger import debug_print

try:
    load_dotenv()
except Exception:
    pass

class TimetableManager:
    BASE_URL = "https://perongo-backend.onrender.com"
    FIREBASE_API_KEY = "AIzaSyA9bVoD8HSCoychV7Qgn1DJmeC6RreBl3o"
    
    _cached_token: str = None

    @classmethod
    async def _get_auth_token(cls) -> str:
        dev_token = os.getenv("CLIENT_SIGNATURE")
        if dev_token:
            return dev_token

        if cls._cached_token:
            return cls._cached_token

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={cls.FIREBASE_API_KEY}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json={"returnSecureToken": True})
                if res.status_code == 200:
                    data = res.json()
                    cls._cached_token = data.get("idToken", "")
                    return cls._cached_token
        except Exception as e:
            debug_print(f"[Auth Error] Nie udało się pobrać tokenu anonimowego: {e}")

        return ""

    @classmethod
    async def get_timetable(
        cls,
        station_name: str,
        station_id: str | int,
        date_str: str = None,
        time_str: str = None,
        is_arrival: bool = False,
        is_web: bool = False
    ) -> tuple[list[dict], str | None]:

        endpoint = f"{cls.BASE_URL}/api/v1/schedules"
        token = await cls._get_auth_token()

        params = {
            "stations": str(station_id),
            "is_arrival": str(is_arrival).lower(),
        }

        if date_str:
            params["date"] = date_str
        if time_str:
            params["time"] = time_str

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(endpoint, params=params, headers=headers)

            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) == 0:
                    return [], _("Brak połączeń dla stacji '{station_name}' (ID: {station_id}).").format(station_name=station_name, station_id=station_id)
                return data, None
            elif res.status_code == 403:
                return [], _("Odmowa dostępu (403): Błąd autoryzacji Firebase.")
            else:
                return [], _("Błąd serwera HTTP {status_code}: {text}").format(status_code=res.status_code, text=res.text)

        except httpx.ConnectError:
            return [], _("Błąd połączenia z backendem.")
        except httpx.TimeoutException:
            return [], _("Błąd przekroczenia czasu (Timeout).")
        except Exception as e:
            return [], _("Błąd: {type_name}\n{error_msg}").format(type_name=type(e).__name__, error_msg=str(e))