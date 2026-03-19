"""
PoE Currency Drop Calculator - Web Version
Flask приложение для расчёта шанса выпадения валюты в Path of Exile
"""

from flask import Flask, render_template, request, jsonify
from dataclasses import dataclass


@dataclass
class DropData:
    """Базовые данные о дропе"""
    BASE_CHANCE_PER_MONSTER_DIVINE = 0.000002  # 1 на 500,000
    BASE_CHANCE_PER_MONSTER_CHAOS = 0.0005  # 1 на 2,000
    
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
        base_chance = (
            self.data.BASE_CHANCE_PER_MONSTER_DIVINE 
            if currency_type == 'divine' 
            else self.data.BASE_CHANCE_PER_MONSTER_CHAOS
        )
        
        map_multiplier = self.data.MAP_TIER_MULTIPLIERS.get(
            map_tier, 
            self.data.MAP_TIER_MULTIPLIERS[16]
        )
        
        iiq_multiplier = 1 + (item_quantity / 100)
        
        chance_per_monster = base_chance * map_multiplier * iiq_multiplier
        chance_at_least_one = 1 - (1 - chance_per_monster) ** monsters_killed
        expected_count = chance_per_monster * monsters_killed
        
        return {
            'chance_percent': round(chance_per_monster * 100, 6),
            'chance_at_least_one': round(chance_at_least_one * 100, 2),
            'expected_count': round(expected_count, 4),
            'map_multiplier': round(map_multiplier, 2),
            'iiq_multiplier': round(iiq_multiplier, 2),
        }


app = Flask(__name__)
calculator = DropCalculator()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    results = calculator.calculate_drop_chance(
        item_quantity=float(data.get('item_quantity', 100)),
        map_tier=int(data.get('map_tier', 16)),
        monsters_killed=int(data.get('monsters_killed', 500)),
        currency_type=data.get('currency_type', 'divine')
    )
    results['currency_name'] = "Divine Orb" if data.get('currency_type') == 'divine' else "Chaos Orb"
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
