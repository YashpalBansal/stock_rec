from flask import Flask
import os

from routes import dashboard, categories, items, purchases

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

app.register_blueprint(dashboard.bp)
app.register_blueprint(categories.bp)
app.register_blueprint(items.bp)
app.register_blueprint(purchases.bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
