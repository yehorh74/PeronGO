import json
import os
import flet as ft
import datetime
import random

from core.i18n import _
from core.logger import debug_print
from core.ads_manager import AdsManager

class HomeScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/home")

        self.ads_manager = AdsManager(app)

        self.selected_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.selected_time = datetime.datetime.now().strftime("%H:%M")
        self.search_type = "departures"
        self.stations = [] 
        self.setup_ui()
        self.load_stations()

    def load_stations(self):
        json_path = os.path.join(os.path.dirname(__file__), "..", "files", "stations.json")
        
        try:
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "stations" in data:
                        raw_stations = data["stations"]
                    else:
                        raw_stations = data
                    
                    excluded_keywords = ["Kharkiv-Pasazhyrskyi", "Khmelnytskyi", "Poltava-Kyivska", "Piatykhatky", "Kyiv-Pasazhyrskyi", "Znamianka", "Kamianske",
                                         "Berlin", "BERLIN -", "Dresden", "Bischofswerda", "Frankfurt", "Frydlant nad Ostravici", "Frenstat pod Radhostem", "Attnang-Puchheim",
                                         "Alt Rosenthal", "Praha Hlavni Nadrazi", "Praha-Liben", "Bratislava Hlavna Stanica", "Dobratice-Vojkovice", "Goerlitz", "Gersdorf(Goerlitz)",
                                         "Angermuende", "Schoenow(Angerm)", "Goerlitz-Rauschwalde", "Hirschfelde", "Kubschuetz", "Suchdol nad Odrou", "Guestrow", "Blumenhagen", "Gorgast",
                                         "Seitschen", "Cesky Tesin", "Moelln(Meckl)"] 
                    
                    self.stations = []
                    for st in raw_stations:
                        name = st["name"] if isinstance(st, dict) else str(st)
                        if any(keyword in name for keyword in excluded_keywords):
                            continue
                        self.stations.append(st)

                    debug_print(f"Pomyślnie załadowano i przefiltrowano stacje. Liczba wpisów: {len(self.stations)}")
            else:
                debug_print(f"Brak pliku stacji pod ścieżką: {json_path}")
        except Exception as ex:
            debug_print(f"Błąd podczas wczytywania stacji: {ex}")

    async def handle_search_submit_ads(self, e):
        should_show_ad = random.random() < 0.7 
        
        if not self.app.page.web and self.app.page.platform.is_mobile() and should_show_ad:
            debug_print("Losowanie: Wyświetlam reklamę Interstitial przed przejściem do wyników.")
            try:
                self.ads_manager.show_interstitial_ad()
            except Exception as ex:
                debug_print(f"Nie udało się pokazać reklamy: {ex}")

        debug_print("Przechodzę do wyników wyszukiwania...")
        await self.handle_search_submit(e)

    async def open_home(self, e):
        await self.app.url_launcher.launch_url(
            "https://yehorh74.github.io/PeronGO/#home",
            mode=ft.LaunchMode.EXTERNAL_APPLICATION
        )

    def setup_ui(self):
        self.info = ft.IconButton(ft.Icons.HELP, on_click=lambda e: self.page.run_task(self.open_home, e))
        self.settings_btn = ft.IconButton(ft.Icons.SETTINGS, on_click=lambda _: self.app.navigate_to("/settings"))

        self.appbar = ft.AppBar(
            leading=self.info,
            title=ft.Text(_("PeronGO")),
            center_title=True,             
            #bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions_padding=10,
            actions=[self.settings_btn]
        )

        self.stations_search = ft.SearchBar(
            bar_leading=ft.IconButton(icon=ft.Icons.TRAIN),
            bar_hint_text=_("Szukaj stacji..."),
            view_hint_text=_("Wybierz stację..."),
            bar_shape=ft.RoundedRectangleBorder(radius=10),
            bar_border_side=ft.BorderSide(width=1, color=ft.Colors.OUTLINE),
            view_elevation=4,
            view_size_constraints=ft.BoxConstraints(max_height=300),
            on_change=self.handle_search_change,
            on_submit=self.handle_station_select,
            on_tap=self.open_search_view,
        )

        self.date_picker = ft.DatePicker(
            first_date=datetime.datetime.now(),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=self.handle_date_change,
        )

        button_style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=8, vertical=5), 
        )

        self.date_btn = ft.OutlinedButton(content=self.selected_date, icon=ft.Icons.CALENDAR_MONTH, on_click=self.open_date_picker, style=button_style, width=float("inf"))

        self.time_picker = ft.TimePicker(
            confirm_text=_("OK"),
            cancel_text=_("Anuluj"),
            error_invalid_text=_("Niepoprawny czas"),
            on_change=self.handle_time_change,
        )

        self.time_btn = ft.OutlinedButton(
            content=self.selected_time, 
            icon=ft.Icons.ACCESS_TIME, 
            on_click=self.open_time_picker,
            style=button_style,
            width=float("inf"),
        )

        self.type_radio_group = ft.RadioGroup(
            value="departures",
            on_change=self.handle_type_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value="departures", label=_("Odjazdy")),
                    ft.Radio(value="arrivals", label=_("Przyjazdy")),
                ],
                spacing=10
            )
        )

        self.submit_btn = ft.FilledButton(
            content=_("Pokaż rozkład"),
            icon=ft.Icons.SEARCH,
            width=float("inf"),  
            on_click=self.handle_search_submit_ads,
        )

        self.title = ft.Text(
                            _("Rozkład jazdy na żywo"),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        )

        self.subtitle = ft.Text(
                            _("Wyszukaj stację, wybierz datę i sprawdź aktualne odjazdy lub przyjazdy pociągów."),
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            text_align=ft.TextAlign.CENTER,
                        )

        header_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.title,
                    self.subtitle,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            margin=ft.Margin.only(bottom=10),
        )

        options_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.date_btn, col={"xs": 6, "md": 3}),
                ft.Container(content=self.time_btn, col={"xs": 6, "md": 3}),
                ft.Container(
                    content=self.type_radio_group, 
                    col={"xs": 12, "md": 6},
                    alignment=ft.Alignment.CENTER
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            run_spacing=10
        )

        search_block = ft.Column(
            width=500, 
            controls=[
                header_container,
                self.stations_search,
                options_row,
                self.submit_btn
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )

        self.centered_container = ft.Container(
            expand=True,  
            alignment=ft.Alignment.TOP_CENTER,
            content=search_block
        )

        is_mobile = self.app.supported and self.app.page.platform.is_mobile()
        
        main_column_controls = [self.centered_container]
        
        if is_mobile:
            self.banner_ad = self.ads_manager.get_new_banner_ad()
            main_column_controls.append(
                ft.Container(
                    content=self.banner_ad,
                    alignment=ft.Alignment.BOTTOM_CENTER,
                    padding=ft.Padding.only(bottom=5)
                )
            )

        self.main_layout = ft.Column(
            expand=True,
            controls=main_column_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.controls = [self.main_layout]

    def get_station_object(self, input_name: str) -> dict | None:
        search_term = input_name.strip().lower()
        for station in self.stations:
            if isinstance(station, dict):
                if station.get("name", "").lower() == search_term:
                    return station
        return None

    async def handle_search_submit(self, e):
        raw_station = self.stations_search.value.strip() if self.stations_search.value else ""
        date = getattr(self, "selected_date", None)
        time = getattr(self, "selected_time", None)
        search_type = getattr(self, "search_type", "departures")

        if not raw_station:
            self.highlight_search_error(True)
            self.show_error_dialog(_("Brak stacji"), _("Musisz wpisać lub wybrać stację z listy."))
            return

        station_obj = self.get_station_object(raw_station)

        if not station_obj:
            self.highlight_search_error(True)
            self.show_error_dialog(
                _("Nie znaleziono stacji"), 
                _("Stacja '{raw_station}' nie znajduje się w naszej bazie. Wybierz stację z listy podpowiedzi.").format(raw_station=raw_station)
            )
            return

        self.highlight_search_error(False)
        
        self.app.show_results(
            station_name=station_obj["name"],
            station_id=station_obj["id"],
            date_str=date,
            time_str=time,
            search_type=search_type
        )

    def highlight_search_error(self, is_error: bool):
        if is_error:
            self.stations_search.bar_border_side = ft.BorderSide(width=2, color=ft.Colors.RED)
        else:
            self.stations_search.bar_border_side = ft.BorderSide(width=1, color=ft.Colors.OUTLINE)
        self.stations_search.update()

    def validate_station_name(self, input_name: str) -> str | None:
        search_term = input_name.strip().lower()

        for station in self.stations:
            name = station["name"] if isinstance(station, dict) else str(station)
            if name.lower() == search_term:
                return name  
        
        return None

    def show_error_dialog(self, title: str, message: str):
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED),
                    ft.Text(title, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Text(message),
            actions=[
                ft.TextButton(_("OK"), on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_date_picker(self, e):
        self.page.show_dialog(self.date_picker)

    def handle_date_change(self, e):
        if e.control.value:
            raw_date = self.date_picker.value
            safe_date = raw_date + datetime.timedelta(hours=12)
            self.selected_date = safe_date.strftime("%Y-%m-%d")
            
            self.date_btn.content = self.selected_date
            self.date_btn.update()
            
            debug_print(f"Zapisano w self.selected_date: {self.selected_date}")

    def open_time_picker(self, e):
        self.page.show_dialog(self.time_picker)

    def handle_time_change(self, e):
        if e.control.value:
            time_val = self.time_picker.value
            self.selected_time = f"{time_val.hour:02d}:{time_val.minute:02d}"
            
            self.time_btn.content = self.selected_time
            self.time_btn.update()
            
            debug_print(f"Zapisano w self.selected_time: {self.selected_time}")

    def handle_type_change(self, e):
        self.search_type = e.control.value
        debug_print(f"Zmieniono typ wyszukiwania na: {self.search_type}")

    async def open_search_view(self, e):
        await self.generate_station_list(query="")
        await self.stations_search.open_view()

    async def handle_search_change(self, e):
        if self.stations_search.bar_border_side.color == ft.Colors.RED:
            self.highlight_search_error(False)
        query = (e.data or "").strip().lower()

        await self.generate_station_list(query=query)
        await self.stations_search.open_view()

    async def generate_station_list(self, query: str):
        filtered_results = []
        for station in self.stations:
            station_name = station["name"] if isinstance(station, dict) else str(station)
            
            if not query or query in station_name.lower():
                filtered_results.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOCATION_ON),
                        title=ft.Text(station_name),
                        on_click=lambda e, name=station_name: self.page.run_task(self.select_station, name)
                    )
                )

                if len(filtered_results) >= 20:
                    break

        self.stations_search.controls = filtered_results
        self.stations_search.update()

    async def select_station(self, station_name: str):
        self.stations_search.value = station_name
        await self.stations_search.close_view(station_name)
        self.stations_search.update()
        debug_print(f"Wybrano stację: {station_name}")

    def handle_station_select(self, e):
        debug_print(f"Zatwierdzono stację: {e.data}")
        
    
