import flet as ft
from core.timetable_manager import TimetableManager

class ResultsScreen(ft.View):
    def __init__(self, app, station_name: str, station_id: str, date_str: str, time_str: str, search_type: str):
        self.app = app
        self.station_name = station_name
        self.station_id = station_id
        self.date_str = date_str
        self.time_str = time_str
        self.is_arrival = (search_type == "arrivals")

        super().__init__(route="/results")
        self.setup_ui()

    def setup_ui(self):
        title_type = "Przyjazdy" if self.is_arrival else "Odjazdy"
        self.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.app.navigate_to("/home")),
            title=ft.Text(f"{title_type}: {self.station_name}"),
            center_title=True,
        )

        self.header_info = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.PRIMARY),
                    ft.Text(f"{self.date_str}", weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=ft.Colors.PRIMARY),
                    ft.Text(f"{self.time_str}", weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            padding=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=8,
            margin=ft.Margin.only(left=15, right=15)
        )

        self.results_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10
        )

        self.loading_indicator = ft.Column(
            controls=[
                ft.ProgressRing(),
                ft.Text("Pobieranie rozkładu z sieci...", size=14, color=ft.Colors.GREY_600)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        self.centered_container = ft.Container(
                    expand=True,  
                    alignment=ft.Alignment.TOP_CENTER,
                    content=self.loading_indicator
                )

        self.controls = [
            self.header_info,
            self.centered_container
        ]

    def did_mount(self):
        self.load_data()

    def load_data(self):
        data = TimetableManager.get_timetable(
            station_name=self.station_name,
            station_id=self.station_id,
            date_str=self.date_str,
            time_str=self.time_str,
            is_arrival=self.is_arrival
        )

        if self.centered_container in self.controls:
            self.controls.remove(self.centered_container)

        if not data:
            self.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.TRAIN_OUTLINED, size=48, color=ft.Colors.GREY_400),
                            ft.Text("Brak połączeń lub błąd połączenia z serwerem.", color=ft.Colors.GREY_600)
                        ],
                        alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.Alignment.TOP_CENTER,
                    expand=True
                )
            )
        else:
            list_view = ft.ListView(expand=True, spacing=10, padding=10)
            for item in data:
                delay_color = ft.Colors.GREEN_600 if item["opoznienie"] == "o czasie" else ft.Colors.RED_600
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(item["godzina"], size=18, weight=ft.FontWeight.BOLD),
                                        ft.Text(item["opoznienie"], size=12, color=delay_color, weight=ft.FontWeight.BOLD)
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    width=75
                                ),
                                ft.VerticalDivider(width=1),
                                ft.Column(
                                    controls=[
                                        ft.Text(item["kierunek"], size=14, weight=ft.FontWeight.BOLD, max_lines=2),
                                        ft.Text(f"Pociąg: {item['pociag']}", size=12, color=ft.Colors.GREY_500)
                                    ],
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text("Peron/Tor", size=10, color=ft.Colors.GREY_500),
                                        ft.Text(item["peron"], size=13, weight=ft.FontWeight.BOLD)
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10
                    )
                )
                list_view.controls.append(card)

            self.controls.append(list_view)

        self.update()