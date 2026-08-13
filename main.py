import os
import flet as ft

from screens.home import HomeScreen
from screens.settings import SettingsScreen
from screens.results_screen import ResultsScreen

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PeronGO"
        self.version = "0.2.1"

        page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("pl", "PL")],
            current_locale=ft.Locale("pl", "PL"),
        )

    async def init_async(self):
        prefs = ft.SharedPreferences()
        
        try:
            saved_theme = await prefs.get("theme_mode") or "system"
        except Exception:
            saved_theme = "system"

        if saved_theme == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        
        self.page.on_route_change = self.route_change
        
        self.page.route = "/home"
        self.route_change(None)

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
    ft.run(main)