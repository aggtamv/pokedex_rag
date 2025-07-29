from poke_app import create_app, db
from poke_app.models import Pokemon
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)