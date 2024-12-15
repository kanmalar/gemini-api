from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def load_data():
  with open(DATA_FILE, "r") as f:
    try:
        return json.load(f)
    except json.JSONDecodeError:
      return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route('/api/items', methods=['GET'])
def get_items():
    """
    Get all items
    ---
    responses:
      200:
        description: A list of items
    """
    data = load_data()
    return jsonify(data)


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
  """
  Get an item by ID
  ---
  parameters:
    - name: item_id
      in: path
      type: integer
      required: true
      description: The ID of the item to retrieve
  responses:
    200:
      description: The item details
    404:
      description: Item not found
  """
  data = load_data()
  for item in data:
      if item['id'] == item_id:
        return jsonify(item)
  return jsonify({'message': 'Item not found'}), 404


@app.route('/api/items', methods=['POST'])
def create_item():
    """
    Create a new item
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
            type: object
            properties:
                name:
                    type: string
                    description: The name of the item
                description:
                    type: string
                    description: The description of the item
    responses:
      201:
        description: Item created
    """
    data = load_data()
    new_item = request.get_json()
    if not new_item:
       return jsonify({'message': 'Invalid item data'}), 400

    if "id" not in new_item or new_item["id"] is None:
       new_id = max([item.get('id', 0) for item in data], default=0) + 1
       new_item['id'] = new_id

    data.append(new_item)
    save_data(data)
    return jsonify(new_item), 201



@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update an existing item
    ---
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: The ID of the item to update
      - in: body
        name: body
        required: true
        schema:
            type: object
            properties:
                name:
                    type: string
                    description: The new name of the item
                description:
                    type: string
                    description: The new description of the item
    responses:
        200:
          description: Item updated
        404:
          description: Item not found
    """
    data = load_data()
    updated_item = request.get_json()
    for index, item in enumerate(data):
        if item['id'] == item_id:
            data[index].update(updated_item)
            save_data(data)
            return jsonify(data[index])
    return jsonify({'message': 'Item not found'}), 404


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Delete an item by ID
    ---
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: The ID of the item to delete
    responses:
      200:
        description: Item deleted
      404:
        description: Item not found
    """
    data = load_data()
    for item in data:
      if item['id'] == item_id:
        data.remove(item)
        save_data(data)
        return jsonify({'message': 'Item deleted'})
    return jsonify({'message': 'Item not found'}), 404


# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "My API Documentation"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Generate swagger spec
from flasgger import Swagger

app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3,
    'specs': [
        {
            'endpoint': 'swagger',
            'route': '/swagger.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
            'definition_filter': lambda definition: True # all in
        }
    ]
}


swagger = Swagger(app)


@app.route('/swagger.json')
def swagger():
    return jsonify(swagger.get_apispecs())

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)