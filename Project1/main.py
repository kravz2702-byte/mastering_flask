import os 
from webapp import create_app
from config import DevConfig

#env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app(DevConfig)

if __name__ == '__main__':
    app.run(debug=True)