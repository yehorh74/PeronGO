import flet as ft
import flet_ads as fta

from core.logger import debug_print

ids = {
    ft.PagePlatform.ANDROID: {
        "banner": "ca-app-pub-5022715823578219/1629350740",
        "interstitial": "ca-app-pub-5022715823578219/5873069271",
    }
}

class AdsManager:
    def __init__(self, app):
        self.app = app

        self._interstitial_ad = None

    def get_new_banner_ad(self) -> fta.BannerAd:
        platform = self.app.page.platform
        banner_id = ids.get(platform, {}).get("banner", "")
        
        return fta.BannerAd(
            unit_id=banner_id,
            width=320,
            height=50,
            on_click=lambda e: debug_print("BannerAd clicked"),
            on_load=lambda e: debug_print("BannerAd loaded successfully"),
            on_error=lambda e: debug_print(f"BannerAd error: {getattr(e, 'data', e)}"),
            on_open=lambda e: debug_print("BannerAd opened"),
            on_close=lambda e: debug_print("BannerAd closed"),
            on_impression=lambda e: debug_print("BannerAd impression"),
            on_will_dismiss=lambda e: debug_print("BannerAd will dismiss"),
        )

    def preload_interstitial_ad(self):
        platform = self.app.page.platform
        interstitial_id = ids.get(platform, {}).get("interstitial", "")

        def handle_load(e):
            debug_print("InterstitialAd preloaded successfully")
            self._interstitial_ad = iad

        def handle_error(e):
            debug_print(f"InterstitialAd preload error: {getattr(e, 'data', e)}")
            self._interstitial_ad = None

        def handle_close(e):
            debug_print("InterstitialAd closed - ładowarka przygotowuje kolejną reklamę")
            self._interstitial_ad = None
            self.preload_interstitial_ad()

        iad = fta.InterstitialAd(
            unit_id=interstitial_id,
            on_load=handle_load,
            on_error=handle_error,
            on_close=handle_close,
            on_click=lambda e: debug_print("InterstitialAd clicked"),
        )

    async def show_interstitial_ad(self):
        if self._interstitial_ad:
            try:
                await self._interstitial_ad.show()
                return True
            except Exception as ex:
                debug_print(f"InterstitialAd show error: {ex}")
                self._interstitial_ad = None
        else:
            debug_print("InterstitialAd nie była jeszcze gotowa - próbuję załadować na szybko.")
            self.preload_interstitial_ad()
        return False