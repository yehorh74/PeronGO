import flet as ft

class SettingsScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/settings")

        self.setup_ui()

    def setup_ui(self):
        self.back_btn = ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.app.navigate_to("/home"))

        self.appbar = ft.AppBar(
            leading=self.back_btn,
            title=ft.Text("USTAWIENIA"),
            center_title=True,             
            #bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            #actions=[self.settings_btn]
        )

        current_mode = self.app.page.theme_mode
        if current_mode == ft.ThemeMode.LIGHT:
            initial_val = "light"
        elif current_mode == ft.ThemeMode.DARK:
            initial_val = "dark"
        else:
            initial_val = "system"

        self.theme_label = ft.Text(
            value="Motyw",
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.system = ft.ListTile(
                                leading=ft.Icon(ft.Icons.SETTINGS_APPLICATIONS),
                                title=ft.Text("Systemowy"),
                                trailing=ft.Radio(value="system"),
                                on_click=lambda _: self._select_radio("system")
                            )

        self.light = ft.ListTile(
                                leading=ft.Icon(ft.Icons.SUNNY),
                                title=ft.Text("Jasny"),
                                trailing=ft.Radio(value="light"),
                                on_click=lambda _: self._select_radio("light")
                            )

        self.dark = ft.ListTile(
                                leading=ft.Icon(ft.Icons.MODE_NIGHT),
                                title=ft.Text("Ciemny"),
                                trailing=ft.Radio(value="dark"),
                                on_click=lambda _: self._select_radio("dark")
                            )

        self.theme_radio_group = ft.RadioGroup(
            value=initial_val,
            on_change=self.change_theme,
            content=ft.Column(
                controls=[
                    self.system,
                    self.light,
                    self.dark,
                ],
                spacing=5
            )
        )

        self.app_info = ft.Text(
            value="Informacja o aplikacji",
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.policy = ft.ListTile(
            leading=ft.Icons.POLICY,
            title="Polityka prywatności",
            on_click=lambda _: print("Dodać link, test")
        )

        self.terms = ft.ListTile(
            leading=ft.Icons.EDIT_DOCUMENT,
            title="Warunki korzystania",
            on_click=lambda _: print("Dodać link, test")
        )

        self.version = ft.Container(
            content=ft.Text(value=self.app.version),
            alignment=ft.Alignment.CENTER,  
            padding=10
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        #ft.Divider(),
                        self.theme_label,
                        self.theme_radio_group,
                        ft.Divider(),
                        self.app_info,
                        self.policy,
                        self.terms,
                        self.version
                    ],
                    spacing=10
                ),
                padding=10
            )
        ]

    def _select_radio(self, val: str):
        self.theme_radio_group.value = val
        self.app.page.run_task(self.change_theme, None)

    async def change_theme(self, e):
        theme_val = self.theme_radio_group.value 

        if theme_val == "light":
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_val == "dark":
            self.app.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app.page.theme_mode = ft.ThemeMode.SYSTEM

        prefs = ft.SharedPreferences()
        await prefs.set("theme_mode", theme_val)
        
        self.app.page.update()

        