import requests
import os
import uvicorn

from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy 
from forms import IngredientForm
from dotenv import load_dotenv
from lxml import html
from reportlab.lib.pagesizes import letter
from fpdf import FPDF
from flask import jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Load environment variables from .env file
load_dotenv()

# Recipe model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.Text, nullable=True)      # Text to store a list of ingredients
    instructions = db.Column(db.Text, nullable=True)      # Text to store instructions
    calories = db.Column(db.Integer, nullable=True)       # Calories information
    image_url = db.Column(db.String(300), nullable=True)  # Store image URL
    recipe_url = db.Column(db.String(300), nullable=True) # Original recipe URL

    def __repr__(self):
        return f"Recipe('{self.name}', '{self.user_id}')"


# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Debugging table
@app.route('/db_check')
def db_check():
    with app.app_context():
        tables = db.engine.table_names()
        return f"Tables in database: {tables}"
    
# Route to get ingredients, send request, return recipes
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
@app.route('/get_recipes', methods=['GET', 'POST'])
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

        # Extract recipe title
        recipe_title = tree.xpath('/html/body/div[4]/div/div[3]/h1/text()')
        recipe_title = recipe_title[0].strip() if recipe_title else 'Title not found'

        # Extract ingredients
        ingredients = tree.xpath('/html/body/div[4]/div/div[3]/div[9]/div/div[2]/div[3]/text()')
        ingredients = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]

        # Extract instructions, with a fallback to another method if the first fails
        instructions = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/ol/li/text()')
        if not instructions:  # Attempt a secondary method
            instructions_div = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/text()')
            instructions = [text.strip() for text in instructions_div if text.strip()]

        # Clean instructions
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
# saves PDF in static folder, locally

# @app.route('/save_pdf', methods=['POST'])
# def save_pdf():
#     recipe_data = session.get('recipe_data')
#     if not recipe_data:
#         flash("No recipe data available to download.", "danger")
#         return redirect(url_for('get_recipes'))

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     # Add title
#     pdf.cell(200, 10, txt=f"Recipe: {recipe_data['title']}", ln=True, align='C')

#     # Add ingredients
#     pdf.cell(200, 10, txt="Ingredients:", ln=True)
#     for ingredient in recipe_data['ingredients']:
#         pdf.cell(200, 10, txt=ingredient, ln=True)

#     # Add instructions
#     pdf.cell(200, 10, txt="Instructions:", ln=True)
#     for instruction in recipe_data['instructions']:
#         pdf.multi_cell(0, 10, txt=instruction)

#     # Save the PDF to a temporary file
#     pdf_filename = f"{recipe_data['title']}.pdf"
#     pdf_path = os.path.join('static', pdf_filename)
#     pdf.output(pdf_path)

#     # Send the PDF file to the user
#     return send_file(pdf_path, as_attachment=True)

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