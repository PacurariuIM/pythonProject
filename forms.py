from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class IngredientForm(FlaskForm):
    ingredients = StringField('Enter main ingredients (comma separated)', validators=[DataRequired()])
    submit = SubmitField('Get Recipes')