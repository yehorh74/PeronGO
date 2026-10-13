import flet as ft
import textwrap
import webbrowser

from core.i18n import _, init_i18n

class SettingsScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/settings")

        self.setup_ui()

    def setup_ui(self):
        self.back_btn = ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.app.navigate_to("/home"))

        self.appbar = ft.AppBar(
            leading=self.back_btn,
            title=ft.Text(_("Ustawienia")),
            center_title=True,             
            #bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            #actions=[self.settings_btn]
        )

        current_lang = self._get_current_lang_code()

        self.language_label = ft.Text(
            value=_("Język"),
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.polish = ft.ListTile(
                                leading=ft.Icon(ft.Icons.LANGUAGE),
                                title=ft.Text(_("Polski")),
                                trailing=ft.Radio(value="pl"),
                                on_click=lambda _: self._select_radio_lang("pl")
                            )

        self.english = ft.ListTile(
                                leading=ft.Icon(ft.Icons.LANGUAGE),
                                title=ft.Text(_("Angielski")),
                                trailing=ft.Radio(value="en"),
                                on_click=lambda _: self._select_radio_lang("en")
                            )

        self.language_radio_group = ft.RadioGroup(
            value=current_lang,
            on_change=self.change_language,
            content=ft.Column(
                controls=[
                    self.polish,
                    self.english,
                ],
                spacing=5
            )
        )

        current_mode = self.app.page.theme_mode
        if current_mode == ft.ThemeMode.LIGHT:
            initial_val = "light"
        elif current_mode == ft.ThemeMode.DARK:
            initial_val = "dark"
        else:
            initial_val = "system"
        
        self.theme_label = ft.Text(
            value=_("Motyw"),
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.system = ft.ListTile(
                                leading=ft.Icon(ft.Icons.SETTINGS_APPLICATIONS),
                                title=ft.Text(_("Systemowy")),
                                trailing=ft.Radio(value="system"),
                                on_click=lambda _: self._select_radio("system")
                            )

        self.light = ft.ListTile(
                                leading=ft.Icon(ft.Icons.SUNNY),
                                title=ft.Text(_("Jasny")),
                                trailing=ft.Radio(value="light"),
                                on_click=lambda _: self._select_radio("light")
                            )

        self.dark = ft.ListTile(
                                leading=ft.Icon(ft.Icons.MODE_NIGHT),
                                title=ft.Text(_("Ciemny")),
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
            value=_("Informacja o aplikacji"),
            size=16,
            weight=ft.FontWeight.BOLD
        )

        self.policy = ft.ListTile(
            leading=ft.Icons.POLICY,
            title=_("Polityka prywatności"),
            on_click=lambda _: webbrowser.open("https://yehorh74.github.io/PeronGO/index.html#privacy")
        )

        self.terms = ft.ListTile(
            leading=ft.Icons.EDIT_DOCUMENT,
            title=_("Warunki korzystania"),
            on_click=lambda _: webbrowser.open("https://yehorh74.github.io/PeronGO/index.html#terms")
        )

        self.version = ft.Container(
            content=ft.Text(value=self.app.version),
            alignment=ft.Alignment.CENTER,  
            padding=10
        )

        licenses_text = textwrap.dedent(_("""
        ### 📜 Licencje i Źródła Danych / Licenses & Data Sources

        **PeronGO** korzysta z otwartych technologii oraz danych publicznych:

        * **[Flet Framework](https://flet.dev)** — Licencja Apache 2.0
        * **[Python](https://www.python.org)** — Licencja Python Software Foundation (PSF)
        * **[Firebase / Google Identity](https://firebase.google.com)** — Usługa uwierzytelniania Google Cloud
        * **[Otwarte dane kolejowe (PKP PLK)](https://pdp-api.plk-sa.pl/)** — Dane o rozkładach jazdy i opóźnieniach pociągów pobierane z publicznie dostępnych interfejsów informacyjnych.

        ---
        *Aplikacja nie jest oficjalną aplikacją PKP PLK. Wszystkie znaki towarowe należą do ich prawnych właścicieli.*
        """))

        self.licenses_markdown = ft.Markdown(
            value=licenses_text,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=self.handle_link_tap,
        )

        self.licenses_card = ft.Container(
            content=self.licenses_markdown,
            padding=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=10,
            margin=ft.Margin.only(top=10)
        )

        self.controls = [
            ft.ListView(
                expand=True,
                padding=15,
                controls=[
                    self.language_label,
                    self.language_radio_group,
                    ft.Divider(),
                    self.theme_label,
                    self.theme_radio_group,
                    ft.Divider(),
                    self.app_info,
                    self.policy,
                    self.terms,
                    ft.Divider(),
                    self.licenses_card,
                    self.version
                ]
            )
        ]

    async def handle_link_tap(self, e):
        await self.app.url_launcher.launch_url(e.data)

    def _select_radio(self, val: str):
        self.theme_radio_group.value = val
        self.app.page.run_task(self.change_theme, None)

    def _select_radio_lang(self, val: str):
        self.language_radio_group.value = val
        self.app.page.run_task(self.change_language, None)

    def _get_current_lang_code(self,) -> str:
        try:
            loc = getattr(self.app.page, "locale_configuration", None)
            if loc and loc.current_locale:
                return "en" if loc.current_locale.language_code == "en" else "pl"
        except Exception:
            pass
        return "pl"

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

    async def change_language(self, e):
        lang_val = self.language_radio_group.value or "pl"

        if hasattr(ft, "LocaleConfiguration"):
            self.app.page.locale_configuration = ft.LocaleConfiguration(
                supported_locales=[ft.Locale("pl", "PL"), ft.Locale("en", "US")],
                current_locale=ft.Locale(lang_val, "PL" if lang_val == "pl" else "US")
            )

        prefs = ft.SharedPreferences()
        await prefs.set("language", lang_val)

        init_i18n(lang_code=lang_val)

        self.app.navigate_to("/settings")

        