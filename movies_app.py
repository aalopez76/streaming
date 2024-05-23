import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)


db = firestore.Client(credentials=creds, project="Streaming")


dbMOVIES = db.collection('movies')

st.header('Nuevo registro')
