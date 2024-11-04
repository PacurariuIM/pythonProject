import requests
import os
from flask import jsonify
import requests
from bs4 import BeautifulSoup


from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, IngredientForm, LoginForm
from dotenv import load_dotenv
from lxml import html


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load environment variables from .env file
load_dotenv()

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Create an instance of the form
    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html', form=form)  # Pass the form to the template


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create an instance of LoginForm
    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html', form=form)  # Pass form to template


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Debugging table
@app.route('/db_check')
def db_check():
    with app.app_context():
        tables = db.engine.table_names()
        return f"Tables in database: {tables}"
    
# Route to get ingredients, send request, return recipes
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
@app.route('/get_recipes', methods=['GET', 'POST'])
@login_required
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

@app.route('/save_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def save_recipe(recipe_id):
    # Retrieve data sent from the form
    recipe_title = request.form.get('recipe_title')
    recipe_image = request.form.get('recipe_image')
    recipe_url = request.form.get('recipe_url')

    # Scrape additional details from the recipe URL
    scraped_data = scrape_recipe(recipe_url)

    if scraped_data:
        # If scraping was successful, create a new Recipe entry
        new_recipe = Recipe(
            user_id=current_user.id,
            name=scraped_data['title'],
            ingredients="\n".join(scraped_data['ingredients']),  # Join list into a single string
            instructions="\n".join(scraped_data['instructions']),
            calories=scraped_data['calories'],
            image_url=recipe_image,
            recipe_url=recipe_url
        )

        # Add and commit the new recipe to the database
        db.session.add(new_recipe)
        db.session.commit()
        
        flash(f'Recipe "{recipe_title}" saved successfully!', 'success')
    else:
        flash("Failed to save the recipe. Please try again later.", 'danger')
    
    return redirect(url_for('get_recipes'))


def scrape_recipe(recipe_url):
    """Scrapes recipe data from the provided recipe URL."""
    response = requests.get(recipe_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        tree = html.fromstring(response.content)

        # Extract recipe title
        recipe_title = tree.xpath('/html/body/div[4]/div/div[3]/h1/text()')
        recipe_title = recipe_title[0].strip() if recipe_title else "Unknown Title"

        # Extract ingredients
        ingredients = tree.xpath('/html/body/div[4]/div/div[3]/div[9]/div/div[2]/div[3]/text()')
        ingredients = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]

        # Extract instructions
        instructions = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/ol/li/text()')
        instructions = [instruction.strip() for instruction in instructions if instruction.strip()]

        # For simplicity, we'll set calories to 0 (can be updated if you can find the path to it)
        calories = 0

        # Return a dictionary with the scraped data
        return {
            'title': recipe_title,
            'ingredients': ingredients,
            'instructions': instructions,
            'calories': calories
        }
    else:
        # If scraping fails, log the error and return None
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
