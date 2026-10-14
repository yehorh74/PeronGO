import os
import sys
import httpx
import platform
from dotenv import load_dotenv

from core.i18n import _
from core.logger import debug_print

try:
    load_dotenv()
except Exception:
    pass

class TimetableManager:
    BASE_URL = "https://perongo-backend.onrender.com"
    
    API_KEY_ANDROID = "AIzaSyA9bVoD8HSCoychV7Qgn1DJmeC6RreBl3o"
    API_KEY_WEB = "AIzaSyAcN5-1Lzq5le7K_nqSosTy9HiKXkQqwrA"
    
    _cached_token: str = None

    @classmethod
    def _get_api_key(cls) -> str:
        is_web = (sys.platform == "emscripten" or platform.system() == "Emscripten")
        
        if is_web:
            return os.getenv("FIREBASE_API_KEY_WEB", cls.API_KEY_WEB)
        else:
            return os.getenv("FIREBASE_API_KEY_ANDROID", cls.API_KEY_ANDROID)

    @classmethod
    async def _get_auth_token(cls) -> str:
        dev_token = os.getenv("CLIENT_SIGNATURE")
        if dev_token:
            debug_print("[Auth Client] Używam lokalnego CLIENT_SIGNATURE")
            return dev_token

        if cls._cached_token:
            debug_print("[Auth Client] Używam zcachowanego tokenu Firebase")
            return cls._cached_token

        api_key = cls._get_api_key()
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        debug_print(f"[Auth Client] Próbuję pobrać nowy token z Firebase (klucz: {api_key[:10]}...)")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json={"returnSecureToken": True})
                debug_print(f"[Auth Client] Odpowiedź Firebase Identity Toolkit: Status {res.status_code}")
                
                if res.status_code == 200:
                    data = res.json()
                    cls._cached_token = data.get("idToken", "")
                    debug_print(f"[Auth Client] Sukces! Pobrano token o długości: {len(cls._cached_token)}")
                    return cls._cached_token
                else:
                    debug_print(f"[Auth Client ERROR] Status {res.status_code}: {res.text}")
        except Exception as e:
            debug_print(f"[Auth Client EXCEPTION] Nie udało się pobrać tokenu: {e}")

        debug_print("[Auth Client ERROR] ❌ Nie udało się uzyskać tokenu, zwracam pusty string!")
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