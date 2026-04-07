import pickle
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import gdown
import os
import joblib

MODEL_PATH = "similarity.pkl"
API_KEY = os.getenv("TMDB_API_KEY")

if not os.path.exists(MODEL_PATH):
    url = "https://drive.google.com/uc?id=1CA0LDm9iBWpVmfIaJfY0Rc_Plz18m1SZ"
    gdown.download(url, MODEL_PATH, quiet=False)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

def get_poster(movie_id, retries=3):
    for attempt in range(retries):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
            data = requests.get(url, timeout=5)
            data.raise_for_status()
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except Exception as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            else:
                print(f"All {retries} attempts failed for movie_id {movie_id}.")
                return "https://placehold.co/300x450?text=No+Poster"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies=[]
    recommended_movie_ids = []
    for i in movies_list:
        recommended_movie_ids.append(movies.iloc[i[0]].id)
        recommended_movies.append(movies.iloc[i[0]].title)
    with ThreadPoolExecutor(max_workers=5) as executor:
        recommended_movies_posters = list(executor.map(get_poster, recommended_movie_ids))
    return recommended_movies, recommended_movies_posters

movies_dict=pickle.load(open('movie_dict.pkl','rb'))
movies=pd.DataFrame(movies_dict)
similarity = model
st.title('Movie Recommendation System')
selected_movie_name = st.selectbox(
"Let's find your next movie!",
movies['title'].values,
)
if st.button("Recommend"):
    with st.spinner("Finding best movies for you..."):
        names,posters = recommend(selected_movie_name)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.caption(names[0])
            st.image(posters[0])
        with col2:
            st.caption(names[1])
            st.image(posters[1])
        with col3:
            st.caption(names[2])
            st.image(posters[2])
        with col4:
            st.caption(names[3])
            st.image(posters[3])
        with col5:
            st.caption(names[4])
            st.image(posters[4])
