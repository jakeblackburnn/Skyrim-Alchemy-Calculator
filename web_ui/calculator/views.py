import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import get_all_ingredients
from src.alchemy_simulator import AlchemySimulator


def calculator_view(request):
    """Main calculator interface with player stats and inventory."""
    ingredients = get_all_ingredients()
    return render(request, 'calculator/calculator.html', {'ingredients': ingredients})


def datasets_view(request):
    """Display ingredients and effects datasets."""
    from .utils import get_all_effects
    ingredients = get_all_ingredients()
    effects = get_all_effects()
    return render(request, 'calculator/datasets.html', {
        'ingredients': ingredients,
        'effects': effects
    })


def insights_view(request):
    """Analysis and insights section (coming soon)."""
    return render(request, 'calculator/insights.html')


@require_http_methods(["POST"])
def calculate_potions(request):
    """API endpoint to calculate potions from player stats and ingredients."""
    try:
        data = json.loads(request.body)

        # Transform frontend data to player_stats dict format
        player_stats = {
            "alchemy_skill": data.get("skill", 15),
            "fortify_alchemy": data.get("fortify", 0),
            "alchemist_perk": data.get("alchemist_rank", 0),
            "physician_perk": data.get("physician", False),
            "benefactor_perk": data.get("benefactor", False),
            "poisoner_perk": data.get("poisoner", False),
            "seeker_of_shadows": data.get("seeker", False),
            "purity_perk": data.get("purity", False),
        }

        ingredients_list = data.get("ingredients", [])

        # Validate ingredients list
        if not ingredients_list or len(ingredients_list) < 2:
            return JsonResponse({
                "error": "Please select at least 2 ingredients"
            }, status=400)

        # Run simulation
        sim = AlchemySimulator(player_stats, ingredients_list)

        # Sort potions by value and serialize
        sorted_potions = sorted(sim.potions, key=lambda p: p.total_value, reverse=True)
        potions_json = [potion.to_dict() for potion in sorted_potions]

        return JsonResponse({"potions": potions_json})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def download_ingredients_csv(request):
    """Download ingredients dataset as CSV."""
    from django.http import FileResponse
    from django.conf import settings

    file_path = settings.PROJECT_ROOT / 'data' / 'master_ingredients.csv'
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename='skyrim_ingredients.csv'
    )


def download_effects_csv(request):
    """Download effects dataset as CSV."""
    from django.http import FileResponse
    from django.conf import settings

    file_path = settings.PROJECT_ROOT / 'data' / 'effects.csv'
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename='skyrim_effects.csv'
    )
