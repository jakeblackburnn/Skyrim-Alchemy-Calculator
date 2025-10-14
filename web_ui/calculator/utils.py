import csv
from django.conf import settings

def get_all_ingredients():
    """Load all ingredients from CSV as list of dicts for template rendering."""
    ingredients_path = settings.PROJECT_ROOT / 'data' / 'master_ingredients.csv'

    with open(ingredients_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # Convert to list and extract only needed fields
        ingredients = []
        for row in reader:
            ingredients.append({
                'name': row['ingredient_name'],
                'value': row['base_value'],
                'weight': row['weight'],
                'effects': [
                    row['effect_1'],
                    row['effect_2'],
                    row['effect_3'],
                    row['effect_4']
                ]
            })
        return ingredients


def get_all_effects():
    """Load all effects from CSV as list of dicts for template rendering."""
    effects_path = settings.PROJECT_ROOT / 'data' / 'effects.csv'

    with open(effects_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        effects = []
        for row in reader:
            effects.append({
                'name': row['effect_name'],
                'base_cost': row['base_cost'],
                'effect_type': row['effect_type'],
                'is_beneficial': row['is_beneficial'],
                'varies_duration': row['varies_duration']
            })
        return effects
