import json
import os
import flet as ft
import datetime

class HomeScreen(ft.View):
    def __init__(self, app):
        self.app = app
        super().__init__(route="/home")

        self.selected_date = datetime.datetime.now().strftime("%Y-%m-%d")
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

        search_block = ft.Column(
            width=500, 
            controls=[
                self.stations_search,
                self.date_btn
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        self.centered_container = ft.Container(
            expand=True,  
            alignment=ft.Alignment.CENTER,
            content=search_block
        )

        self.controls = [self.centered_container]

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

    async def open_search_view(self, e):
        query = (self.stations_search.value or "").strip().lower()
        if len(query) >= 2:
            await self.stations_search.open_view()

    async def handle_search_change(self, e):
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
        print(f"Wybrano stację: {station_name}")

    def handle_station_select(self, e):
        print(f"Zatwierdzono stację: {e.data}")
        
    
