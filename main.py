import os
import flet as ft

from screens.home import HomeScreen
from screens.settings import SettingsScreen

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PeronGO"

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

        self.page.update()

async def main(page: ft.Page):
    app = App(page)
    await app.init_async()

if __name__ == "__main__":
    ft.run(main)