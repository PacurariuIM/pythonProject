import requests
from lxml import html

# URL of the recipe page
url = 'https://spoonacular.com/recipes/Mushroom-Gnocchi-652672'  # Replace with the actual URL



# Send a GET request to the web page
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    tree = html.fromstring(response.content)

    # Extract recipe title
    recipe_title = tree.xpath('/html/body/div[4]/div/div[3]/h1/text()')[0].strip()

    # Extract ingredients
    ingredients = tree.xpath('/html/body/div[4]/div/div[3]/div[9]/div/div[2]/div[3]/text()')
    
    # Clean the list to remove any empty strings and leading/trailing spaces
    ingredients = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]

    # Extract instructions
    instructions = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/ol/li/text()')
    instructions = [instruction.strip() for instruction in instructions if instruction.strip()]

    # Create a dictionary to store the recipe data
    recipe_data = {
        'title': recipe_title,
        'ingredients': ingredients,
        'instructions': instructions
    }

    # Print the recipe data
    print(recipe_data)
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
