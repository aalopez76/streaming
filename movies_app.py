import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Conexión a Firestore usando credenciales JSON
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streaming-4e657")

dbMovies = db.collection('movies')

# Título de la aplicación en Streamlit
st.title('Netflix app')

# Función para cargar datos desde Firestore con caché
@st.cache_data
def load_data():
  data_ref = list(db.collection(u'movies').stream())
  data_dict = list(map(lambda x: x.to_dict(), data_ref))
  data = pd.DataFrame(data_dict)
  return data

# Cargar datos usando la función
data = load_data()

# Checkbox para mostrar todos los filmes
if st.sidebar.checkbox('Mostrar todos los filmes'):
    st.subheader('Todos los filmes')
    st.dataframe(data)

# Variable de estado para controlar la ejecución de la búsqueda
if 'search_executed' not in st.session_state:
    st.session_state.search_executed = False

# Buscar filmes por título
st.sidebar.header('Buscar filmes')
search_title = st.sidebar.text_input('Título del filme')
search_button = st.sidebar.button('Buscar filmes')

def search_films():
    filtered_data = data[data['name'].str.contains(search_title, case=False, na=False)]
    if filtered_data.empty:
        st.write('No se encontraron filmes con ese título.')
    else:
        st.write(f'{len(filtered_data)} filme(s) encontrado(s).')
        st.dataframe(filtered_data)

# Ejecutar búsqueda
if search_button:
    search_films()


# Buscar filmes por director
st.sidebar.header('Buscar filmes por director')
director = st.sidebar.selectbox('Seleccione un director', data['director'].unique())
search_button = st.sidebar.button('Filtrar Director')

# Función para filtrar datos por director
def filter_by_director(selected_director):
    return data[data['director'] == selected_director]

# Botón de búsqueda por director
if search_button:
    filtered_data = filter_by_director(director)
    total_films = len(filtered_data)
    if total_films == 0:
        st.write('No se encontraron filmes para este director.')
    else:
        st.write(f'{total_films} filme(s) encontrado(s).')
        st.dataframe(filtered_data)

# Insersión de un nuevo filme
st.sidebar.header('Nuevo filme')

name = st.sidebar.text_input('Name')
company = st.sidebar.text_input('Company')
director = st.sidebar.text_input('Director')
genre = st.sidebar.text_input('Genre')

# Botón para agregar un nuevo filme
if st.sidebar.button('Crear nuevo filme'):
    if name and company and director and genre:
        new_film = {'name': name, 'company': company, 'director': director, 'genre': genre}
        try:
            db.collection('movies').add(new_film)  # Inserta el nuevo filme en Firestore
            st.sidebar.success('Filme agregado exitosamente!')
            st.write("Nuevo filme agregado: ", new_film)
            load_data.clear_cache()
        except Exception as e:
            st.sidebar.error(f'Error al agregar el filme: {e}')
    else:
        st.sidebar.error('Por favor, completa todos los campos.')
