import streamlit as st
import pandas as pd
import pickle
import requests
from streamlit_option_menu import option_menu


st.set_page_config(page_title="Movie's Database", layout="wide")
st.markdown("<h1 style='text-align: center; color: Dark Gray;'>Movie's Databse</h1>",
            unsafe_allow_html=True)


def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


@st.cache()
def initial_load():
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    countvec = CountVectorizer(max_features=8000, stop_words='english')
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    vectors = countvec.fit_transform(movies_dict['tags']).toarray()
    cosine_similarity = cosine_similarity(vectors)
    movies = pd.DataFrame(movies_dict)

    top_50_movies = pd.read_csv("Top_50_movies.csv")
    trending_posters = [fetch_poster(x) for x in top_50_movies['id']]
    df = pd.read_csv('Filtering_movies.csv')
    return(movies, cosine_similarity, top_50_movies, trending_posters, df)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


movies, cosine_similarity, top_50_movies, trending_posters, df = initial_load()


def best_one(df):
    import math
    x1 = (df['vote_count']//1000 + 1) * 7109
    x2 = df['vote_count'] % 1000 * 7
    x3 = df['vote_average']*13
    return math.log(x1+x2+x3)


def select(df, selection):
    df = pd.read_csv('Filtering_movies.csv')
    for i in selection:
        df = df[df[i] == 1]

    df = df[['id', 'title', 'vote_count', 'vote_average']]
    if df.empty:
        return df
    df['sorting_column'] = df.apply(lambda x: best_one(x), axis=1)
    return df.sort_values('sorting_column', ascending=False).head(10)

st.write("##")
# tab1, tab2, tab3, tab4 = st.tabs(
#     ['Trending Movies', 'Movie Recommendations','Filtering movies on the basis of Genres', "Get in Touch with Me"]
# )

selected_tab = option_menu(
    menu_title = None,
    options = ['Trending Movies', 'Movie Recommendations','Filtering movies on Genres', "Get in Touch with Me"],
    icons = ['graph-up-arrow','hand-thumbs-up','funnel','envelope-open'],
    menu_icon = 'cast',
    default_index = 0,
    orientation = 'horizontal',
    styles={
        "icon": {"font-size": "20px"},
        "nav-link": {"font-size": "18px"}
    }
)

st.write("##")

if selected_tab == 'Trending Movies':

    col1, col2, col3, col4, col5 = st.columns(5)
    for i in range(10):
        with col1:
            st.text(str(i*5+1) + ". " + top_50_movies['title'][i*5])
            st.image(trending_posters[i*5], width=200)
        with col2:
            st.text(str(i*5+2) + ". " + top_50_movies['title'][i*5+1])
            st.image(trending_posters[i*5+1], width=200)
        with col3:
            st.text(str(i*5+3) + ". " + top_50_movies['title'][i*5+2])
            st.image(trending_posters[i*5+2], width=200)
        with col4:
            st.text(str(i*5+4) + ". " + top_50_movies['title'][i*5+3])
            st.image(trending_posters[i*5+3], width=200)
        with col5:

            st.text(str(i*5+5) + ". " + top_50_movies['title'][i*5+4])
            st.image(trending_posters[i*5+4], width=200)

    st.markdown("<h6 style='text-align: center; color: Dark Gray;'>Made with the help of TMDB API...</h6>",
                unsafe_allow_html=True)


elif selected_tab == 'Movie Recommendations':

    def recommend(given):
        movie_index = movies[movies['title'] == given].index[0]
        distances = cosine_similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)),
                            reverse=True, key=lambda x: x[1])[1:6]

        r_movies = []
        movie_posters = []

        for i in movie_list:

            r_movies.append(movies['title'][i[0]])
            movie_posters.append(fetch_poster(movies['id'][i[0]]))

        return r_movies, movie_posters

    selection = st.selectbox(
        "Enter the name of the movie you want recommendations for:",
        movies['title'].values
    )

    if st.button('Recommend Movies !', help='Click on it to get movie recommendations'):
        st.write(" ")
        names, posters = recommend(selection)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.text(names[0])
            st.image(posters[0],width = 200)

        with col2:
            st.text(names[1])
            st.image(posters[1], width = 200)

        with col3:
            st.text(names[2])
            st.image(posters[2], width = 200)

        with col4:
            st.text(names[3])
            st.image(posters[3], width = 200)

        with col5:
            st.text(names[4])
            st.image(posters[4], width = 200)

        st.write()
        st.markdown(
            "<h6 style='text-align: center; color: Dark Gray;'>Made with the help of TMDB API...</h6>", unsafe_allow_html=True)


elif selected_tab == 'Filtering movies on Genres':

    option_selection = st.multiselect(
        "Select the generes",
        ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Foreign',
            'History', 'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western']
    )
    if st.button("Filter Movies"):
        filter_df = select(df,option_selection)
        if filter_df.empty:
            st.write("")
            st.markdown("<h4 style='text-align: center; color: Dark Gray;'>Sorry, We can't find any movie according to your selections...</h4>", unsafe_allow_html=True)
        else: 
            filter_df = filter_df[['id','title']]
            posters = []
            name = []
            for i in filter_df['id']:
                print(i)
                posters.append(fetch_poster(i))
            for i in filter_df['title']:
                name.append(i)
            print(posters)
            col1, col2, col3, col4, col5 = st.columns(5)
            st.write('') 
            for i in range(2):
                try:
                    with col1:
                        st.text(str(i*5+1) + ". " + name[i*5])
                        st.image(posters[i*5], width=200)
                    with col2:
                        st.text(str(i*5+2) + ". " + name[i*5+1])
                        st.image(posters[i*5+1], width=200)
                    with col3:
                        st.text(str(i*5+3) + ". " + name[i*5+2])
                        st.image(posters[i*5+2], width=200)
                    with col4:
                        st.text(str(i*5+4) + ". " + name[i*5+3])
                        st.image(posters[i*5+3], width=200)
                    with col5:
                        st.text(str(i*5+5) + ". " + name[i*5+4])
                        st.image(posters[i*5+4], width=200)
                except:pass
                st.write(' ')
            st.markdown("<h6 style='text-align: center; color: Dark Gray;'>Made with the help of TMDB API...</h6>", unsafe_allow_html=True)


elif selected_tab == 'Get in Touch with Me':
    st.write("##")
    # st.subheader(":mailbox: Get in Touch With Me...!")
    contact_form = '''
        <form action="https://formsubmit.co/tokas.2sonu@gmail.com" method="POST">
            <input type="hidden" name="_autoresponse" value="Thank You for spending your valuable time on my website. I will contact you soon.">
            <input type="hidden" name="_template" value="table">
            <input type="hidden" name="_next" value="https://vivek-2567-movie-recommendation-system-app-ir5ih5.streamlit.app">
            <input type="text" name="name" id = 'input' placeholder = "Your Name" required>
            <input type="email" name="email" id = 'input' placeholder = "Your Email" required>
            <textarea name = 'message' id = 'input' placeholder = 'Your Message' required></textarea>
            <button onclick="document.getElementById('input').value = ''" type="submit">Send</button>
        </form>
    '''
    st.markdown(contact_form,unsafe_allow_html=True)
    local_css("style/style.css")

