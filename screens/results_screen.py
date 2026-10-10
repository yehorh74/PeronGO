import asyncio
from datetime import datetime
import flet as ft
from core.timetable_manager import TimetableManager

class ResultsScreen(ft.View):
    REFRESH_INTERVAL = 120

    def __init__(self, app, station_name: str, station_id: str, date_str: str, time_str: str, search_type: str):
        self.app = app
        self.station_name = station_name
        self.station_id = station_id
        self.date_str = date_str
        self.time_str = time_str
        self.is_arrival = (search_type == "arrivals")
        
        self.is_running = False
        self.is_paused = False  

        super().__init__(route="/results")
        self.setup_ui()

    def setup_ui(self):
        title_type = "Przyjazdy" if self.is_arrival else "Odjazdy"
        self.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.app.navigate_to("/home")),
            title=ft.Text(f"{title_type}: {self.station_name}"),
            center_title=True,
        )

        self.live_time_text = ft.Text(self.time_str, weight=ft.FontWeight.BOLD)
        self.last_update_text = ft.Text("Ostatnia aktualizacja: --:--:--", size=11, color=ft.Colors.GREY_500)

        self.header_info = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.PRIMARY),
                            ft.Text(f"{self.date_str}", weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=ft.Colors.PRIMARY),
                            self.live_time_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    ft.Row(
                        controls=[self.last_update_text],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=4
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

        self.main_content = ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            content=self.loading_indicator
        )

        self.controls = [
            self.header_info,
            self.main_content
        ]

    def did_mount(self):
        self.is_running = True
        
        self.page.on_app_lifecycle_state_change = self._handle_lifecycle_change

        self.page.run_task(self._clock_loop)
        self.page.run_task(self._initial_load_and_start_loop)

    def will_unmount(self):
        self.is_running = False
        if self.page:
            self.page.on_app_lifecycle_state_change = None
        super().will_unmount()

    def _handle_lifecycle_change(self, e: ft.AppLifecycleStateChangeEvent):
        state_str = str(e.state).lower()
        if "pause" in state_str or "hidden" in state_str or "inactive" in state_str:
            self.is_paused = True
            print("[Lifecycle] Aplikacja w tle - wstrzymano odświeżanie.")
        elif "resume" in state_str or "show" in state_str:
            self.is_paused = False
            print("[Lifecycle] Aplikacja na wierzchu - wznowiono odświeżanie.")

    async def _clock_loop(self):
        while self.is_running:
            now_str = datetime.now().strftime("%H:%M:%S")
            if self.live_time_text.value != now_str:
                self.live_time_text.value = now_str
                self.live_time_text.update()
            await asyncio.sleep(1)

    async def _initial_load_and_start_loop(self):
        await self.refresh_timetable_data(is_initial=True)
        
        while self.is_running:
            await asyncio.sleep(self.REFRESH_INTERVAL)
            if not self.is_running:
                break
            
            if self.is_paused:
                continue

            current_time = datetime.now().strftime("%H:%M")
            await self.refresh_timetable_data(time_override=current_time, is_initial=False)

    async def refresh_timetable_data(self, time_override: str = None, is_initial: bool = False):
        is_web_platform = getattr(self.page, "web", False) if self.page else False
        fetch_time = time_override or self.time_str

        data, error_msg = await TimetableManager.get_timetable(
            station_name=self.station_name,
            station_id=self.station_id,
            date_str=self.date_str,
            time_str=fetch_time,
            is_arrival=self.is_arrival,
            is_web=is_web_platform
        )

        if not self.is_running:
            return

        if error_msg or not data:
            if is_initial or self.main_content.content == self.loading_indicator:
                message = error_msg if error_msg else "Brak połączeń dla wybranej stacji."
                icon = ft.Icons.ERROR_OUTLINE if error_msg else ft.Icons.TRAIN_OUTLINED
                icon_color = ft.Colors.RED_400 if error_msg else ft.Colors.GREY_400

                self.main_content.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(icon, size=48, color=icon_color),
                            ft.Text(message, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.Alignment.TOP_CENTER,
                    expand=True
                )
                self.main_content.update()
            else:
                self.last_update_text.value = f"Błąd odświeżania ({datetime.now().strftime('%H:%M:%S')})"
                self.last_update_text.color = ft.Colors.RED_400
                self.last_update_text.update()
        else:
            cards = self._build_cards(data)
            self.results_list.controls = cards

            if self.main_content.content != self.results_list:
                self.main_content.content = self.results_list
                self.main_content.update()
            else:
                self.results_list.update()

            self.last_update_text.value = f"Ostatnia aktualizacja: {datetime.now().strftime('%H:%M:%S')}"
            self.last_update_text.color = ft.Colors.GREY_500
            self.last_update_text.update()

    def _build_cards(self, data: list[dict]) -> list[ft.Control]:
        cards = []
        for item in data:
            delay = item.get("opoznienie", "o czasie")
            delay_color = ft.Colors.GREEN_600 if delay == "o czasie" else ft.Colors.RED_600
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(item.get("godzina", "--:--"), size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(delay, size=12, color=delay_color, weight=ft.FontWeight.BOLD)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                width=75
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                controls=[
                                    ft.Text(item.get("kierunek", "Brak informacji"), size=14, weight=ft.FontWeight.BOLD, max_lines=2),
                                    ft.Text(f"Pociąg: {item.get('pociag', '-')}", size=12, color=ft.Colors.GREY_500)
                                ],
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Peron/Tor", size=10, color=ft.Colors.GREY_500),
                                    ft.Text(item.get("peron", "-/-"), size=13, weight=ft.FontWeight.BOLD)
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
            cards.append(card)
        return cards