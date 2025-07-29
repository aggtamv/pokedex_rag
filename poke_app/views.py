from flask import Blueprint, render_template, render_template, request, jsonify, flash, redirect, url_for, session, current_app, send_file
from flask_login import login_required, current_user
import logging
import os
from gradio_client import Client, handle_file
import pandas as pd
from werkzeug.utils import secure_filename
from .config import Config
import plotly.express as px
import plotly
import json
import requests
from .models import Pokemon

views = Blueprint("views", __name__)

@views.route("/home")
@views.route("/")
@login_required
def home():
    pokemon_list = Pokemon.query.all()
    return render_template('index.html', pokemon_list=pokemon_list)


@views.route('/pokemon/<int:pokemon_id> ', methods=['GET'])
@login_required
def show_pokemon(pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return "Pokemon not found", 404

    data = res.json()
    pokemon = {
        'id': data['id'],
        'name': data['name'].capitalize(),
        'sprite': data['sprites']['front_default'],
        'height': data['height'],
        'weight': data['weight'],
        'abilities': [a['ability']['name'] for a in data['abilities']],
        'types': [t['type']['name'].capitalize() for t in data['types']],
        'moves': [m['move']['name'] for m in data['moves']],
        'cry_url': f"https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{pokemon_id}.ogg"
    }

    print(f"Pokemon data fetched: {pokemon}")

    # Send name to RAG agent
    try:
        response = requests.post(
            "http://localhost:8000/ask",  # your FastAPI RAG endpoint
            json={"question": f"Give me full Pokédex info about {pokemon['name']}"}
        )
        if response.ok:
            print(response.json())
            pokedex_entry = response.json().get("answer", "")
        else:
            print(response.json())
            pokedex_entry = "Could not fetch Pokédex info from AI."
    except Exception as e:
        pokedex_entry = f"Error: {str(e)}"

    print(f"Pokédex entry fetched: {pokedex_entry}")
    return render_template('detail.html', pokemon=pokemon, pokedex_entry=pokedex_entry)

@views.route('/pokemon/<int:pokemon_id>/json')
@login_required
def get_pokemon_json(pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return jsonify({'error': 'Pokemon not found'}), 404

    data = res.json()
    pokemon = {
        'id': data['id'],
        'name': data['name'].capitalize(),
        'sprite': data['sprites']['front_default'],
        'height': data['height'],
        'weight': data['weight'],
        'abilities': [a['ability']['name'] for a in data['abilities']],
        'types': [t['type']['name'].capitalize() for t in data['types']],
        'moves': [m['move']['name'] for m in data['moves']],
        'cry_url': f"https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{pokemon_id}.ogg"
    }
    return jsonify(pokemon)




