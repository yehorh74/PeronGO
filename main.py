import os
import flet as ft
from screens.home import HomeScreen

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PeronGO"
        self.page.theme_mode = ft.ThemeMode.DARK
        
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

        self.page.update()

def main(page: ft.Page):
    App(page)

if __name__ == "__main__":
    ft.run(main)