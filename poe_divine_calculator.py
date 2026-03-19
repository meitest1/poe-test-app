"""
Path of Exile - Divine Orb Drop Chance Calculator
Калькулятор шанса выпадения Divine Orb в зависимости от параметров карты
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from dataclasses import dataclass


@dataclass
class DropData:
    """Базовые данные о дропе"""
    # Базовый шанс выпадения Divine/Exalted Orb (примерный, по данным сообщества)
    BASE_CHANCE_PER_MONSTER_DIVINE = 0.000002  # 1 на 500,000
    
    # Базовый шанс выпадения Chaos Orb (примерный, по данным сообщества)
    # Chaos Orb выпадает значительно чаще Divine Orb
    BASE_CHANCE_PER_MONSTER_CHAOS = 0.0005  # 1 на 2,000 (примерно)
    
    # Множители для разных tier карт (в игре T1-T16 + T17 в 3.25)
    MAP_TIER_MULTIPLIERS = {
        1: 0.3, 2: 0.35, 3: 0.4, 4: 0.45, 5: 0.5,
        6: 0.55, 7: 0.6, 8: 0.65, 9: 0.7, 10: 0.75,
        11: 0.8, 12: 0.85, 13: 0.9, 14: 0.95, 15: 1.0,
        16: 1.15, 17: 1.25
    }


class DropCalculator:
    """Калькулятор шанса выпадения валюты"""
    
    def __init__(self):
        self.data = DropData()
    
    def calculate_drop_chance(self, item_quantity: float, map_tier: int, 
                              monsters_killed: int = 100, 
                              currency_type: str = 'divine') -> dict:
        """
        Расчёт шанса выпадения валюты
        
        Args:
            item_quantity: Процент увеличения количества предметов (IIQ)
            map_tier: Tier карты (1-17)
            monsters_killed: Количество убитых монстров
            currency_type: 'divine' или 'chaos'
            
        Returns:
            dict с результатами расчёта
        """
        # Базовый шанс в зависимости от типа валюты
        base_chance = (
            self.data.BASE_CHANCE_PER_MONSTER_DIVINE 
            if currency_type == 'divine' 
            else self.data.BASE_CHANCE_PER_MONSTER_CHAOS
        )
        
        # Получаем множитель от tier карты
        map_multiplier = self.data.MAP_TIER_MULTIPLIERS.get(
            map_tier, 
            self.data.MAP_TIER_MULTIPLIERS[16]  # По умолчанию T16
        )
        
        # IIQ влияет линейно: +100% IIQ = x2 к шансу дропа
        iiq_multiplier = 1 + (item_quantity / 100)
        
        # Базовый шанс на одного монстра с учётом множителей
        chance_per_monster = (
            base_chance
            * map_multiplier 
            * iiq_multiplier
        )
        
        # Шанс получить хотя бы один за N монстров
        # Формула: 1 - (1 - p)^n
        chance_at_least_one = 1 - (1 - chance_per_monster) ** monsters_killed
        
        # Ожидаемое количество
        expected_count = chance_per_monster * monsters_killed
        
        # Сколько монстров нужно убить для 50% шанса
        monsters_for_50_percent = 0.693 / chance_per_monster if chance_per_monster > 0 else float('inf')
        
        return {
            'chance_per_monster': chance_per_monster,
            'chance_percent': chance_per_monster * 100,
            'chance_at_least_one': chance_at_least_one * 100,
            'expected_count': expected_count,
            'monsters_for_50_percent': monsters_for_50_percent,
            'map_multiplier': map_multiplier,
            'iiq_multiplier': iiq_multiplier,
        }


class CalculatorApp:
    """GUI приложение калькулятора"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PoE Currency Drop Calculator")
        self.root.geometry("650x750")
        self.root.resizable(True, True)
        
        self.calculator = DropCalculator()
        self.current_currency = 'divine'
        
        self._setup_styles()
        self._create_widgets()
        self._calculate()
    
    def _setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Result.TLabel', font=('Segoe UI', 11))
        style.configure('Highlight.TLabel', font=('Segoe UI', 11, 'bold'), 
                       foreground='#FFD700')
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="📊 PoE Currency Calculator",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # === Выбор валюты ===
        currency_frame = ttk.Frame(main_frame)
        currency_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Label(currency_frame, text="Валюта:").pack(side=tk.LEFT, padx=5)
        
        self.currency_var = tk.StringVar(value='divine')
        
        divine_radio = ttk.Radiobutton(
            currency_frame,
            text="Divine Orb",
            variable=self.currency_var,
            value='divine'
        )
        divine_radio.pack(side=tk.LEFT, padx=10)
        
        chaos_radio = ttk.Radiobutton(
            currency_frame,
            text="Chaos Orb",
            variable=self.currency_var,
            value='chaos'
        )
        chaos_radio.pack(side=tk.LEFT, padx=10)

        # Привязка всех переменных для авто-пересчёта
        self.currency_var.trace_add('write', lambda *args: self._calculate())
        
        # === Параметры ввода ===
        
        # Map Tier
        ttk.Label(main_frame, text="Tier карты:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.map_tier_var = tk.IntVar(value=16)
        self.map_tier_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.map_tier_var,
            values=list(range(1, 18)),  # T1-T17
            width=10,
            state='readonly'
        )
        self.map_tier_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.map_tier_var.trace_add('write', lambda *args: self._calculate())
        
        # Item Quantity
        ttk.Label(main_frame, text="Item Quantity (%):").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.item_quantity_var = tk.IntVar(value=100)
        self.item_quantity_scale = ttk.Scale(
            main_frame,
            from_=0,
            to=500,
            variable=self.item_quantity_var,
            orient=tk.HORIZONTAL
        )
        self.item_quantity_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        self.quantity_label = ttk.Label(
            main_frame,
            text="100%",
            width=6
        )
        self.quantity_label.grid(row=3, column=2, sticky=tk.W, padx=5)
        self.item_quantity_var.trace_add('write', lambda *args: self._calculate())
        
        # Monsters Killed
        ttk.Label(main_frame, text="Убито монстров:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.monsters_var = tk.IntVar(value=500)
        self.monsters_entry = ttk.Entry(
            main_frame,
            textvariable=self.monsters_var,
            width=15
        )
        self.monsters_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.monsters_var.trace_add('write', lambda *args: self._calculate())
        
        # === Результаты ===

        results_frame = ttk.LabelFrame(
            main_frame,
            text="Результаты",
            padding="10"
        )
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        results_frame.columnconfigure(1, weight=1)
        
        # Шанс на монстра (%)
        ttk.Label(results_frame, text="Шанс с монстра:").grid(
            row=0, column=0, sticky=tk.W, pady=3
        )
        self.chance_label = ttk.Label(
            results_frame,
            text="-",
            style='Result.TLabel'
        )
        self.chance_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=3)
        
        # Шанс хотя бы один (%)
        ttk.Label(results_frame, text="Шанс хотя бы 1:").grid(
            row=1, column=0, sticky=tk.W, pady=3
        )
        self.chance_at_least_label = ttk.Label(
            results_frame,
            text="-",
            style='Highlight.TLabel'
        )
        self.chance_at_least_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=3)
        
        # Ожидаемое количество
        ttk.Label(results_frame, text="Ожидаемое количество:").grid(
            row=2, column=0, sticky=tk.W, pady=3
        )
        self.expected_label = ttk.Label(
            results_frame,
            text="-",
            style='Result.TLabel'
        )
        self.expected_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=3)
        
        # Множители
        multipliers_frame = ttk.LabelFrame(
            main_frame,
            text="Множители",
            padding="10"
        )
        multipliers_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        multipliers_frame.columnconfigure(1, weight=1)
        
        ttk.Label(multipliers_frame, text="Множитель Tier карты:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.map_mult_label = ttk.Label(multipliers_frame, text="-")
        self.map_mult_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        
        ttk.Label(multipliers_frame, text="Множитель IIQ:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.iiq_mult_label = ttk.Label(multipliers_frame, text="-")
        self.iiq_mult_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
        
        # === Информация ===
        
        info_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            wrap=tk.WORD,
            font=('Segoe UI', 9)
        )
        info_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        info_content = """
📌 Информация:
• Divine Orb и Exalted Orb имеют одинаковый базовый шанс выпадения (подтверждено GGG)
• Chaos Orb выпадает значительно чаще Divine Orb (~1 на 2,000 дропов)
• Item Quantity (IIQ) прямо пропорционально увеличивает шанс выпадения валюты
• Item Rarity (IIR) НЕ влияет на шанс выпадения валюты
• Map Tier влияет через уровень монстров (T16-T17 дают максимальный шанс)

⚠️ Примечание: Точные дроп-рейты не раскрываются разработчиками. 
Расчёты основаны на данных сообщества и могут отличаться от реальных значений.
        """
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
    
    def _update_quantity_label(self):
        """Обновление метки количества предметов"""
        self.quantity_label.config(text=f"{self.item_quantity_var.get()}%")
        self._calculate()
    
    def _calculate(self):
        """Выполнение расчёта"""
        try:
            map_tier = self.map_tier_var.get()
            item_quantity = self.item_quantity_var.get()
            monsters_killed = int(self.monsters_var.get())
            currency_type = self.currency_var.get()
            
            results = self.calculator.calculate_drop_chance(
                item_quantity=item_quantity,
                map_tier=map_tier,
                monsters_killed=monsters_killed,
                currency_type=currency_type
            )
            
            # Название валюты для отображения
            currency_name = "Divine Orb" if currency_type == 'divine' else "Chaos Orb"
            
            # Обновление результатов
            self.chance_label.config(
                text=f"{results['chance_percent']:.6f}%"
            )
            self.chance_at_least_label.config(
                text=f"{results['chance_at_least_one']:.2f}%"
            )
            self.expected_label.config(
                text=f"{results['expected_count']:.4f} {currency_name}"
            )
            
            # Множители
            self.map_mult_label.config(text=f"x{results['map_multiplier']:.2f}")
            self.iiq_mult_label.config(text=f"x{results['iiq_multiplier']:.2f}")
            
        except (ValueError, tk.TclError):
            pass  # Игнорируем ошибки при вводе


def main():
    """Точка входа приложения"""
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
