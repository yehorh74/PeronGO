set -o errexit

echo "--- Pobieranie i instalacja Flutter SDK dla Render ---"
git clone https://github.com/flutter/flutter.git -b stable --depth 1 _flutter
export PATH="$PATH:$(pwd)/_flutter/bin"

flutter config --no-analytics
flutter precache --web

echo "--- Instalacja zależności Pythona ---"
pip install --upgrade pip
pip install flet==0.86.5

echo "--- Budowanie aplikacji Flet Web ---"
flet build web --build-number 1 -o dist/web