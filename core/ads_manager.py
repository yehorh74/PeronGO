import flet as ft
import flet_ads as fta

from core.logger import debug_print

ids = {
    ft.PagePlatform.ANDROID: {
        "banner": "ca-app-pub-3940256099942544/9214589741",
        "interstitial": "ca-app-pub-3940256099942544/1033173712",
    }
}

class AdsManager:
    def __init__(self, app):
        self.app = app

    def get_new_banner_ad(self) -> fta.BannerAd:
        platform = self.app.page.platform
        banner_id = ids.get(platform, {}).get("banner", "ca-app-pub-3940256099942544/9214589741")
        
        return fta.BannerAd(
            unit_id=banner_id,
            width=320,
            height=50,
            on_click=lambda e: debug_print("BannerAd clicked"),
            on_load=lambda e: debug_print("BannerAd loaded"),
            on_error=lambda e: debug_print("BannerAd error", e.data),
            on_open=lambda e: debug_print("BannerAd opened"),
            on_close=lambda e: debug_print("BannerAd closed"),
            on_impression=lambda e: debug_print("BannerAd impression"),
            on_will_dismiss=lambda e: debug_print("BannerAd will dismiss"),
        )

    def show_interstitial_ad(self):
        platform = self.app.page.platform
        interstitial_id = ids.get(platform, {}).get("interstitial", "ca-app-pub-3940256099942544/1033173712")

        async def show_iad(e: ft.Event[fta.InterstitialAd]):
            try:
                await iad.show()
            except Exception as ex:
                debug_print(f"InterstitialAd show error: {ex}")

        iad = fta.InterstitialAd(
            unit_id=interstitial_id,
            on_load=show_iad,
            on_error=lambda e: debug_print("InterstitialAd error", e.data),
            on_open=lambda e: debug_print("InterstitialAd opened"),
            on_close=lambda e: debug_print("InterstitialAd closed"),
            on_impression=lambda e: debug_print("InterstitialAd impression"),
            on_click=lambda e: debug_print("InterstitialAd clicked"),
        )

