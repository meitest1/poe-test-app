# PoE Currency Drop Calculator

Калькулятор шанса выпадения валюты (Divine Orb, Chaos Orb) в Path of Exile.

## 📁 Файлы

- `poe_divine_calculator.py` — Desktop версия (Tkinter)
- `poe_web/` — Web версия (Flask)
- `Dockerfile` — Для запуска в Docker

## 🖥️ Desktop версия

### Требования
- Python 3.x
- Tkinter (встроен в Python на Windows)

### Запуск
```bash
python poe_divine_calculator.py
```

### Создать .exe
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "PoE Calculator" poe_divine_calculator.py
```

## 🌐 Web версия

### Требования
- Python 3.x
- Flask

### Запуск
```bash
cd poe_web
pip install -r requirements.txt
python app.py
```

Открыть в браузере: http://localhost:5000

## 🐳 Docker

### Сборка
```bash
cd poe_web
docker build -t poe-calculator .
```

### Запуск
```bash
docker run -p 5000:5000 poe-calculator
```

Открыть в браузере: http://localhost:5000

## 📊 Как работает

| Параметр | Влияние |
|----------|---------|
| **Map Tier** | Множитель от 0.3x (T1) до 1.25x (T17) |
| **Item Quantity** | Линейный множитель: +100% IIQ = x2 к шансу |
| **Item Rarity** | НЕ влияет на валюту |

## ⚠️ Примечание

Точные дроп-рейты не раскрываются разработчиками. Расчёты основаны на данных сообщества:
- Divine Orb: ~1 на 500,000 дропов
- Chaos Orb: ~1 на 2,000 дропов

## 📄 Лицензия

MIT
