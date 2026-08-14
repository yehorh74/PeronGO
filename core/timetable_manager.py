import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime

class TimetableManager:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "X-Requested-With": "XMLHttpRequest"
    }

    @staticmethod
    def get_timetable(
        station_name: str,
        station_id: str,
        date_str: str = None,
        time_str: str = None,
        is_arrival: bool = False,
        is_web: bool = False  
    ) -> list[dict]:
        przyjazd_val = "true" if is_arrival else "false"
        
        params = {
            "nazwa": station_name,
            "stacja": station_id,
            "przyjazd": przyjazd_val,
            "_csrf": "scotty.vs_liveticker",
            "evaId": station_id
        }

        if date_str and time_str:
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                params["data"] = dt.strftime("%d%m%Y%H%M")
                params["time"] = dt.strftime("%H:%M")
            except Exception as e:
                print(f"[!] Błąd formatowania daty: {e}. Używam domyślnego zapytania BILKOM.")

        target_url = "https://bilkom.pl/stacje/tablica"

        if is_web:
            req_prep = httpx.Request("GET", target_url, params=params)
            full_url = str(req_prep.url)
            
            final_url = f"https://corsproxy.io/?{full_url}"
            final_params = None 
        else:
            final_url = target_url
            final_params = params

        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(final_url, headers=TimetableManager.HEADERS, params=final_params)

            if res.status_code != 200:
                print(f"[-] Błąd HTTP: {res.status_code}")
                return []
        except Exception as e:
            print(f"[-] Błąd połączenia: {e}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        wiersze = soup.find_all('li', class_=lambda c: c and 'el' in c)
        if not wiersze:
            wiersze = soup.select('li')

        odjazdy = []

        for row in wiersze:
            text_raw = row.get_text(" ", strip=True)
            if "Pokaż szczegóły" not in text_raw and "Kup bilet" not in text_raw and not re.search(r'\d{2}:\d{2}', text_raw):
                continue

            match_czas = re.search(r'(\d{2}:\d{2})', text_raw)
            godzina = match_czas.group(1) if match_czas else "--:--"

            diff_elem = row.find(attrs={"data-difference": True})
            if diff_elem and diff_elem.get("data-difference"):
                diff = diff_elem["data-difference"]
                opoznienie = f"{diff} min" if diff != "0" else "o czasie"
            else:
                opoznienie = "o czasie"

            czysty_tekst = text_raw
            for smiec in ["Pokaż szczegóły", "Kup bilet na ten pociąg", "Kup bilet"]:
                czysty_tekst = czysty_tekst.replace(smiec, "")
            
            czysty_tekst = re.sub(r'\d{1,2}\s+[a-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+', '', czysty_tekst, flags=re.IGNORECASE)

            match_pociag = re.search(r'([A-ZĘÓĄŚŁŻŹNĆ]{1,3}\s*\d{3,6})', czysty_tekst)
            pociag = match_pociag.group(1) if match_pociag else "Pociąg"

            match_peron = re.search(r'([I|V|X]{1,4}\/\d{1,2})', czysty_tekst)
            peron = match_peron.group(1) if match_peron else "-/-"

            kierunek = czysty_tekst.replace(godzina, "").replace(pociag, "").replace(peron, "").strip()
            kierunek = re.sub(r'\b\d{6,}\b', '', kierunek)
            kierunek = re.sub(r'\s+', ' ', kierunek).strip()

            odjazdy.append({
                "godzina": godzina,
                "opoznienie": opoznienie,
                "pociag": pociag,
                "peron": peron,
                "kierunek": kierunek
            })
        
        return odjazdy