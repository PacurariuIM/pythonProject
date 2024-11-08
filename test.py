import requests
from lxml import html

# URL of the recipe page
url = 'https://spoonacular.com/recipes/The-Scotch-Egg-663338'  # Replace with the actual URL

# Send a GET request to the web page
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    tree = html.fromstring(response.content)

    # Extract recipe title
    recipe_title = tree.xpath('/html/body/div[4]/div/div[3]/h1/text()')[0]

    # Extract ingredients
    ingredients = tree.xpath('/html/body/div[4]/div/div[3]/div[9]/div/div[2]/div[3]/text()')
    ingredients = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]

    # Attempt to extract instructions from two different variants
    instructions = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/ol/li/text()')
    if not instructions:  # If the first attempt fails, try the second variant
        instructions_div = tree.xpath('/html/body/div[4]/div/div[3]/div[8]/div/div/text()')
        instructions = [text.strip() for text in instructions_div if text.strip()]

    # Clean the instructions to ensure formatting is proper
    instructions = [instruction for instruction in instructions if instruction]

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
