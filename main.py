import requests
import os
import uvicorn

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy 
from forms import IngredientForm
from dotenv import load_dotenv
from lxml import html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)

# Load environment variables from .env file
load_dotenv()

# Debugging table
# @app.route('/db_check')
# def db_check():
#     with app.app_context():
#         tables = db.engine.table_names()
#         return f"Tables in database: {tables}"
    
# Route to get ingredients, send request, return recipes
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
@app.route('/', methods=['GET', 'POST'])
def get_recipes():
    form = IngredientForm()
    recipes = None
    if form.validate_on_submit():
        # Get ingredients from the form
        ingredients = form.ingredients.data
        # Make a request to Spoonacular API
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=9&apiKey={SPOONACULAR_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            recipes = response.json()  # List of recipes returned by the API
        else:
            flash('Failed to fetch recipes. Please try again.', 'danger')
    
    return render_template('get_recipes.html', form=form, recipes=recipes)

def scrape_recipe(url):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)

        # Extract recipe title dynamically based on tag (e.g., <h1>) and itemprop or class
        recipe_title = tree.xpath('//h1[contains(@itemprop, "name")]/text()')
        recipe_title = recipe_title[0].strip() if recipe_title else 'Title not found'

        # Initialize ingredients list (set to avoid duplicates)
        ingredients = set()

        # Dynamically search for all ingredient sections with the class 'spoonacular-ingredient'
        ingredient_sections = tree.xpath('//div[contains(@class, "spoonacular-ingredient")]')

        for section in ingredient_sections:
            # Search for quantity and ingredient name within the section
            quantity_metric = section.xpath('.//div[contains(@class, "spoonacular-metric")]/text()')
            quantity_us = section.xpath('.//div[contains(@class, "spoonacular-us")]/text()')
            name = section.xpath('.//div[contains(@class, "spoonacular-name")]/text()')

            # Prioritize metric; fallback to US if available
            quantity = quantity_metric[0].strip() if quantity_metric else (quantity_us[0].strip() if quantity_us else '')
            name = name[0].strip() if name else 'Unknown ingredient'

            if quantity and name:
                ingredients.add(f"{quantity} {name}")

        # Convert the set back to a list and optionally sort it
        ingredients = list(ingredients)

        # Instructions Extraction - Dynamically search for instructions divs
        instructions = []

        # Primary search: for recipe instructions (class-based or itemprop-based)
        instruction_div = tree.xpath('//div[contains(@class, "recipeInstructions")]')
        if instruction_div:
            instructions_text = instruction_div[0].text_content().strip()
            instructions = instructions_text.split('\n')  # Split by new lines to separate steps
            instructions = [step.strip() for step in instructions if step.strip()]

        # Fallback search for alternative instruction divs (using itemprop)
        if not instructions:
            alternative_instruction_div = tree.xpath('//div[@itemprop="recipeInstructions"]')
            if alternative_instruction_div:
                instructions_text = alternative_instruction_div[0].text_content().strip()
                instructions = instructions_text.split('\n')  # Split by new lines to separate steps
                instructions = [step.strip() for step in instructions if step.strip()]

        # Fallback for detailed instructions (e.g., if the recipe links elsewhere)
        if not instructions:
            detailed_instructions = tree.xpath('//p[contains(@id, "detailedInstructionsMention")]')
            if detailed_instructions:
                instructions = [p.text.strip() for p in detailed_instructions if p.text.strip()]

        # Exclude any instruction containing "Read the detailed instructions on..."
        instructions = [instruction for instruction in instructions if "Read the detailed instructions on" not in instruction]

        # Clean up empty instructions and compile the data
        instructions = [instruction for instruction in instructions if instruction]

        # Create a dictionary to store the recipe data
        recipe_data = {
            'title': recipe_title,
            'ingredients': ingredients,
            'instructions': instructions
        }

        return recipe_data
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

@app.route('/recipe', methods=['POST'])
def recipe():
    recipe_url = request.form.get('recipe_url')
    if recipe_url:
        recipe_data = scrape_recipe(recipe_url)
        if recipe_data:
            # Sanitize recipe data
            recipe_data['ingredients'] = [
                ingredient.replace('\n', ' ').replace('"', "'") for ingredient in recipe_data['ingredients']
            ]
            recipe_data['instructions'] = [
                instruction.replace('\n', ' ').replace('"', "'") for instruction in recipe_data['instructions']
            ]
            return render_template('recipe.html', recipe=recipe_data)
    flash('Invalid recipe URL or failed to scrape data.', 'danger')
    return redirect(url_for('get_recipes'))


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

# if __name__ == '__main__':
#     app.run(debug=True)