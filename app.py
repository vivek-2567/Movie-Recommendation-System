import streamlit as st
import pandas as pd
import pickle
import requests

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
countvec = CountVectorizer(max_features=8000,stop_words='english')

st.set_page_config(page_title="Recommendation System", layout="wide")
st.markdown("<h1 style='text-align: center; color: White;'>Movie Recommendation System</h1>", unsafe_allow_html=True)


def fetch_poster (movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


movies_dict = pickle.load(open ('movie_dict.pkl','rb'))
vectors = countvec.fit_transform(movies_dict['tags']).toarray()
cosine_similarity = cosine_similarity(vectors)
movies = pd.DataFrame(movies_dict)

def recommend(given):
    movie_index = movies[movies['title'] == given].index[0]
    distances = cosine_similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)),reverse=True,key = lambda x: x[1])[1:6]

    r_movies = []
    movie_posters = []

    for i in movie_list:

        r_movies.append(movies['title'][i[0]])
        movie_posters.append(fetch_poster(movies['id'][i[0]]))
    
    return r_movies,movie_posters

selection = st.selectbox(
    "Enter the name of the movie you want recommendations for:",
    movies['title'].values
)


if st.button('Recommend Movies !',help = 'Click on it to get movie recommendations'):
    st.write(" ")
    names, posters = recommend(selection)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])

    st.write()
    st.markdown("<h6 style='text-align: center; color: White;'>Made with the help of TMDB API...</h6>", unsafe_allow_html=True)


