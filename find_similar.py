import numpy as np
import pandas as pd


def load_embeddings():
    item_factors = np.load('item_factors.npy')
    item_biases = np.load('item_biases.npy')
    return item_factors, item_biases


def find_similar_artists(artist=None, num_items=10, item_lookup=None, item_factors=None, item_biases=None):
    if item_factors is None or item_biases is None:
        item_factors, item_biases = load_embeddings()

    # Get the item id for the given artist
    item_id = int(item_lookup[item_lookup.artist_name == artist]['artist_id'])

    # Get the item vector for our item_id and transpose it.
    item_vec = item_factors[item_id].T

    # Calculate the similarity between the given artist and all other artists
    # by multiplying the item vector with our item_matrix
    scores = np.add(item_factors.dot(item_vec), item_biases).reshape(1, -1)[0]

    # Get the indices for the top num_items scores
    top_indices = np.argsort(scores)[::-1][:num_items]

    # We then use our lookup table to grab the names of these indices
    # and add it along with its score to a pandas dataframe.
    artists, artist_scores = [], []

    for idx in top_indices:
        artists.append(item_lookup.artist_name.loc[item_lookup.artist_id == str(idx)].iloc[0])
        artist_scores.append(scores[idx])

    similar = pd.DataFrame({'artist': artists, 'score': artist_scores})

    return artists
