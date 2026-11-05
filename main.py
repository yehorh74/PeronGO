import os
import warnings
import flet as ft
import flet_ads as fta

from screens.home import HomeScreen
from screens.settings import SettingsScreen
from screens.results_screen import ResultsScreen

from core.i18n import init_i18n, _
from core.logger import debug_print

warnings.filterwarnings("ignore", category=RuntimeWarning)

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = _("PeronGO")
        page.window.icon = "assets/icon.png"
        self.version = "1.0.0"

        self.prefs = ft.SharedPreferences()
        self.url_launcher = ft.UrlLauncher()
        self.current_search_params = None

        self.supported = not page.web and page.platform.is_mobile()
        if self.supported:
            self.consent_manager = fta.ConsentManager()
            page.services.append(self.consent_manager)
        else:
            self.consent_manager = None

    async def init_async(self):      
        try:
            saved_lang = await self.prefs.get("language") or "pl"
        except Exception:
            saved_lang = "pl"

        init_i18n(lang_code=saved_lang)

        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("pl", "PL"), ft.Locale("en", "US")],
            current_locale=ft.Locale(saved_lang, "PL" if saved_lang == "pl" else "US")
        )

        try:
            saved_theme = await self.prefs.get("theme_mode") or "system"
        except Exception:
            saved_theme = "system"

        if saved_theme == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        if self.supported and self.consent_manager:
            await self.init_consent()
        
        self.page.on_route_change = self.route_change
        
        self.page.route = "/home"
        self.route_change(None)

    async def init_consent(self):
        try:
            await self.consent_manager.request_consent_info_update(
                fta.ConsentRequestParameters(
                    consent_debug_settings=fta.ConsentDebugSettings(
                        debug_geography=fta.DebugGeography.EEA,
                    ),
                )
            )
            await self.consent_manager.load_and_show_consent_form_if_required()
            
            can_request = await self.consent_manager.can_request_ads()
            debug_print(f"[CONSENT] Czy można zażądać reklam: {can_request}")
            
        except Exception as ex:
            debug_print(f"[CONSENT ERROR] Błąd podczas pobierania zgody: {ex}")

    async def show_privacy_options_form(self):
        if self.supported and self.consent_manager:
            try:
                await self.consent_manager.show_privacy_options_form()
            except Exception as ex:
                debug_print(f"[PRIVACY FORM ERROR]: {ex}")

    def navigate_to(self, route_name: str):
        self.page.route = route_name
        self.route_change(None)

    def route_change(self, e):
        self.page.views.clear()

        if self.page.route == "/home" or self.page.route == "/":
            self.page.views.append(HomeScreen(self))

        elif self.page.route == "/settings":
            self.page.views.append(SettingsScreen(self))

        elif self.page.route == "/results":
            if self.current_search_params:
                self.page.views.append(
                    ResultsScreen(
                        app=self,
                        station_name=self.current_search_params["station_name"],
                        station_id=self.current_search_params["station_id"],
                        date_str=self.current_search_params["date_str"],
                        time_str=self.current_search_params["time_str"],
                        search_type=self.current_search_params["search_type"],
                    )
                )
            else:
                self.page.route = "/home"
                self.page.views.append(HomeScreen(self))

        self.page.update()

    def show_results(self, station_name, station_id, date_str, time_str, search_type):
        debug_print("==========================================")
        debug_print(f"[MAIN DEBUG] Nazwa stacji: '{station_name}' (typ: {type(station_name)})")
        debug_print(f"[MAIN DEBUG] ID stacji:    '{station_id}' (typ: {type(station_id)})")
        debug_print(f"[MAIN DEBUG] Data:         '{date_str}'")
        debug_print(f"[MAIN DEBUG] Czas:         '{time_str}'")
        debug_print(f"[MAIN DEBUG] Typ:          '{search_type}'")
        debug_print("==========================================", flush=True)
        self.current_search_params = {
            "station_name": station_name,
            "station_id": station_id,
            "date_str": date_str,
            "time_str": time_str,
            "search_type": search_type,
        }
        self.navigate_to("/results")

async def main(page: ft.Page):
    app = App(page)
    await app.init_async()

if __name__ == "__main__":
    ft.run(main, web_renderer=ft.WebRenderer.AUTO)