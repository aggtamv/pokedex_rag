import requests
from poke_app import create_app
from poke_app.models import Pokemon
from poke_app.extensions import db

app = create_app()

def fetch_and_store_pokemon():
    with app.app_context():
        db.drop_all()     # WARNING: removes all data – use with caution
        db.create_all()

        for id in range(1, 387):
            res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
            if res.status_code == 200:
                data = res.json()
                pkmn = Pokemon(
                    id=data['id'],
                    name=data['name'].capitalize(),
                    sprite=data['sprites']['front_default'],
                    height=data['height'],
                    weight=data['weight'],
                    types=', '.join([t['type']['name'].capitalize() for t in data['types']]),
                    abilities=', '.join([a['ability']['name'] for a in data['abilities']])
                )
                db.session.add(pkmn)
        
        db.session.commit()
        print("All Pokémon scraped and stored.")

if __name__ == "__main__":
    fetch_and_store_pokemon()
