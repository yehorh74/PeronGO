import json
import os
import flet as ft
import datetime

class HomeScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/home")

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
                        self.stations = data["stations"]
                    else:
                        self.stations = data
                    print(f"Pomyślnie załadowano stacje. Liczba wpisów: {len(self.stations)}")
            else:
                print(f"Brak pliku stacji pod ścieżką: {json_path}")
        except Exception as ex:
            print(f"Błąd podczas wczytywania stacji: {ex}")

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

        self.stations_search = ft.SearchBar(
            bar_leading=ft.IconButton(icon=ft.Icons.TRAIN),
            bar_hint_text="Szukaj stacji...",
            view_hint_text="Wybierz stację...",
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

        self.date_btn = ft.OutlinedButton(content=self.selected_date, icon=ft.Icons.CALENDAR_MONTH, on_click=self.open_date_picker)

        self.time_picker = ft.TimePicker(
            confirm_text="OK",
            cancel_text="Anuluj",
            error_invalid_text="Niepoprawny czas",
            on_change=self.handle_time_change,
        )

        self.time_btn = ft.OutlinedButton(
            content=self.selected_time, 
            icon=ft.Icons.ACCESS_TIME, 
            on_click=self.open_time_picker
        )

        self.type_radio_group = ft.RadioGroup(
            value="departures",
            on_change=self.handle_type_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value="departures", label="Odjazdy"),
                    ft.Radio(value="arrivals", label="Przyjazdy"),
                ],
                spacing=10
            )
        )

        self.submit_btn = ft.FilledButton(
            content="Pokaż rozkład",
            icon=ft.Icons.SEARCH,
            width=float("inf"),  
            on_click=self.handle_search_submit,
        )

        self.title = ft.Text(
                            "Rozkład jazdy na żywo",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        )

        self.subtitle = ft.Text(
                            "Wyszukaj stację, wybierz datę i sprawdź aktualne odjazdy lub przyjazdy pociągów.",
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

        search_block = ft.Column(
            width=500, 
            controls=[
                header_container,
                self.stations_search,
                ft.Row(
                    controls=[
                        self.date_btn,
                        self.time_btn,
                        ft.Container(expand=True),
                        self.type_radio_group
                    ]
                ),
                self.submit_btn
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        self.centered_container = ft.Container(
            expand=True,  
            alignment=ft.Alignment.CENTER,
            content=search_block
        )

        self.controls = [self.centered_container]

    def handle_search_submit(self, e):
        raw_station = self.stations_search.value.strip() if self.stations_search.value else ""
        date = getattr(self, "selected_date", None)
        time = getattr(self, "selected_time", None)
        search_type = getattr(self, "search_type", "departures")

        if not raw_station:
            self.highlight_search_error(True)
            self.show_error_dialog("Brak stacji", "Musisz wpisać lub wybrać stację z listy.")
            return

        matched_station = self.validate_station_name(raw_station)

        if not matched_station:
            self.highlight_search_error(True)
            self.show_error_dialog(
                "Nie znaleziono stacji", 
                f"Stacja '{raw_station}' nie znajduje się w naszej bazie. Wybierz stację z listy podpowiedzi."
            )
            return

        self.highlight_search_error(False)
        self.stations_search.value = matched_station  #
        self.stations_search.update()

        print(f"Pomyślnie wybrano stację: {matched_station} | Data: {date} | Czas: {time} | Typ: {search_type}")
        # self.app.navigate_to("/results")

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
                ft.TextButton("OK", on_click=close_dialog)
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
            
            print(f"Zapisano w self.selected_date: {self.selected_date}")

    def open_time_picker(self, e):
        self.page.show_dialog(self.time_picker)

    def handle_time_change(self, e):
        if e.control.value:
            time_val = self.time_picker.value
            self.selected_time = f"{time_val.hour:02d}:{time_val.minute:02d}"
            
            self.time_btn.content = self.selected_time
            self.time_btn.update()
            
            print(f"Zapisano w self.selected_time: {self.selected_time}")

    def handle_type_change(self, e):
        self.search_type = e.control.value
        print(f"Zmieniono typ wyszukiwania na: {self.search_type}")

    async def open_search_view(self, e):
        query = (self.stations_search.value or "").strip().lower()
        if len(query) >= 2:
            await self.stations_search.open_view()

    async def handle_search_change(self, e):
        if self.stations_search.bar_border_side.color == ft.Colors.RED:
            self.highlight_search_error(False)
        query = e.data.strip().lower()

        if len(query) < 2:
            self.stations_search.controls = []
            self.stations_search.close_view(self.stations_search.value)
            return

        await self.stations_search.open_view()

        filtered_results = []
        for station in self.stations:
            station_name = station["name"] if isinstance(station, dict) else str(station)
            
            if query in station_name.lower():
                filtered_results.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOCATION_ON),
                        title=ft.Text(station_name),
                        on_click=lambda _, name=station_name: self.select_station(name)
                    )
                )

                if len(filtered_results) >= 20:
                    break

        self.stations_search.controls = filtered_results
        self.stations_search.update()

    def select_station(self, station_name: str):
        self.stations_search.value = station_name
        self.stations_search.close_view(station_name)
        self.stations_search.update()
        print(f"Wybrano stację: {station_name}")

    def handle_station_select(self, e):
        print(f"Zatwierdzono stację: {e.data}")
        
    
