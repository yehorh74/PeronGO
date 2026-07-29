import flet as ft

class HomeScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/home")

        self.setup_ui()

    def setup_ui(self):
        self.info = ft.IconButton(ft.Icons.HELP)
        self.settings_btn = ft.IconButton(ft.Icons.SETTINGS, on_click=lambda _: self.app.navigate_to("/settings"))

        self.appbar = ft.AppBar(
            leading=self.info,
            title=ft.Text("PeronGO"),
            center_title=True,             
            #bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions_padding=10,
            actions=[self.settings_btn]
        )
    
