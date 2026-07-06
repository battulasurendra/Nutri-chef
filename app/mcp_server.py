import os
import sys
from mcp.server.fastmcp import FastMCP

# Create an MCP server instance named "nutri-chef-mcp"
mcp = FastMCP("nutri-chef-mcp")

# Simple mock database for demonstration
RECIPES_DB = [
    {
        "name": "Keto Avocado and Egg Salad",
        "meal_type": "Breakfast",
        "description": "A delicious, low-carb avocado egg salad packed with healthy fats.",
        "ingredients": ["eggs", "avocado", "mayonnaise", "lemon juice", "salt", "pepper"],
        "recipe": "Boil 2 eggs, chop them, and mix with a mashed avocado, 1 tbsp mayonnaise, and a squeeze of lemon juice. Season with salt and pepper."
    },
    {
        "name": "Pan-Seared Salmon with Broccoli",
        "meal_type": "Dinner",
        "description": "Rich in Omega-3s, this simple salmon recipe is both healthy and filling.",
        "ingredients": ["salmon", "broccoli", "olive oil", "garlic", "salt", "lemon"],
        "recipe": "Sear salmon in olive oil for 4 mins per side. Steam broccoli, toss with garlic, olive oil, and lemon juice."
    },
    {
        "name": "Lemon Rosemary Grilled Chicken",
        "meal_type": "Lunch",
        "description": "Tender grilled chicken breast marinated with lemon and rosemary.",
        "ingredients": ["chicken", "lemon juice", "rosemary", "olive oil", "garlic", "salt"],
        "recipe": "Marinate chicken in lemon juice, rosemary, olive oil, garlic, and salt. Grill or bake for 20 minutes until cooked through."
    },
    {
        "name": "Spinach & Feta Egg Muffins",
        "meal_type": "Breakfast",
        "description": "Easy make-ahead breakfast muffins containing protein and fresh greens.",
        "ingredients": ["eggs", "spinach", "feta cheese", "onion", "salt", "pepper"],
        "recipe": "Whisk eggs with chopped spinach and feta. Pour into muffin tin, bake at 350F for 18-20 minutes."
    },
    {
        "name": "Quinoa & Avocado Salad",
        "meal_type": "Lunch",
        "description": "High-fiber quinoa salad with fresh avocado, cherry tomatoes, and vinaigrette.",
        "ingredients": ["quinoa", "avocado", "tomatoes", "olive oil", "lemon juice", "salt"],
        "recipe": "Cook quinoa. Mix with chopped avocado, halved tomatoes, olive oil, lemon juice, and a pinch of salt."
    }
]

SUBSTITUTES_DB = {
    "mayonnaise": "Greek yogurt or mashed avocado",
    "butter": "Coconut oil or olive oil",
    "heavy cream": "Coconut milk or Greek yogurt",
    "sugar": "Stevia, erythritol, or monk fruit sweetener",
    "pasta": "Zucchini noodles (zoodles) or spaghetti squash",
    "rice": "Cauliflower rice",
    "milk": "Almond milk, oat milk, or coconut milk"
}

NUTRITION_DB = {
    "avocado": {"calories": 160, "protein": "2g", "carbs": "8.5g", "fat": "15g"},
    "chicken": {"calories": 165, "protein": "31g", "carbs": "0g", "fat": "3.6g"},
    "salmon": {"calories": 208, "protein": "22g", "carbs": "0g", "fat": "13g"},
    "eggs": {"calories": 155, "protein": "13g", "carbs": "1.1g", "fat": "11g"},
    "spinach": {"calories": 23, "protein": "2.9g", "carbs": "3.6g", "fat": "0.4g"},
    "broccoli": {"calories": 34, "protein": "2.8g", "carbs": "7g", "fat": "0.4g"},
    "quinoa": {"calories": 120, "protein": "4.4g", "carbs": "21g", "fat": "1.9g"}
}

# ==========================================
# MCP Tool Definitions
# ==========================================

@mcp.tool()
def search_recipes(query: str) -> dict:
    """Searches the cookbook database for recipes matching a search term/keyword.
    
    Args:
        query: The search term or keyword (e.g. 'chicken', 'low-carb', 'egg')
    """
    query_lower = query.lower().strip()
    results = []
    
    for r in RECIPES_DB:
        if (query_lower in r["name"].lower() or 
            query_lower in r["meal_type"].lower() or
            query_lower in r["description"].lower() or
            any(query_lower in ing.lower() for ing in r["ingredients"])):
            results.append(r)
            
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }

@mcp.tool()
def get_pantry_items() -> dict:
    """Retrieves the list of currently available pantry items."""
    # Mocking standard pantry contents
    pantry = ["eggs", "spinach", "avocado", "lemon juice", "olive oil", "garlic", "salt", "pepper", "onions"]
    return {
        "pantry": pantry,
        "count": len(pantry)
    }

@mcp.tool()
def get_substitutes(ingredient: str) -> dict:
    """Returns recommended healthy alternatives/substitutes for a given ingredient.
    
    Args:
        ingredient: The ingredient name to find substitutes for (e.g. 'mayonnaise', 'sugar')
    """
    ing_lower = ingredient.lower().strip()
    substitute = SUBSTITUTES_DB.get(ing_lower)
    
    if substitute:
        return {
            "ingredient": ingredient,
            "has_substitute": True,
            "substitute": substitute
        }
    return {
        "ingredient": ingredient,
        "has_substitute": False,
        "message": f"No common healthy substitute found for '{ingredient}'."
    }

@mcp.tool()
def get_nutritional_info(food_item: str) -> dict:
    """Returns estimated calories and macronutrient stats for a food item per 100g.
    
    Args:
        food_item: The food item name to query (e.g. 'salmon', 'avocado', 'chicken')
    """
    food_lower = food_item.lower().strip()
    info = NUTRITION_DB.get(food_lower)
    
    if info:
        return {
            "item": food_item,
            "found": True,
            "nutrition": info
        }
    return {
        "item": food_item,
        "found": False,
        "message": f"Nutritional data not found for '{food_item}'."
    }

if __name__ == "__main__":
    # Run using stdio transport
    mcp.run()
