#!/usr/bin/env bash
set -o errexit

echo "--- Pobieranie Flutter SDK (wersja 3.44.8) ---"
git clone https://github.com/flutter/flutter.git -b 3.44.8 --depth 1 _flutter
export PATH="$PATH:$(pwd)/_flutter/bin"

flutter config --no-analytics
flutter precache --web

echo "--- Instalacja zależności Pythona ---"
pip install --upgrade pip
pip install flet==0.86.5

echo "--- Budowanie aplikacji Flet Web ---"
export FLET_NON_INTERACTIVE="true"
flet build web --web-renderer html --build-number 1 -o dist/web