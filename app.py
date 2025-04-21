import streamlit as st
import re
import json
import PyPDF2
from datetime import datetime
from gsheets import GSheetsManager
import os

# --- Inicialização das cotas ---
VAGAS_TOTAIS = 50
LISTA_ESPERA_MAX = 63  # 50 + 25%
COTAS = {
    "PCD": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("PCD", "")).upper() == "SIM"},
    "RAÇA": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("Etnia", "")).upper() in ["PRETA", "PARDA", "INDÍGENA"]},
    "GÊNERO": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("Gênero", "")).upper() in ["FEMININO", "NÃO BINÁRIO", "NAO BINARIO"]},
    "LGBTQIA+": {"percentual": 5, "preenchidas": 0, "critério": lambda d: str(d.get("LGBTQIA+", "")).upper() == "SIM"},
    "AMPLA": {"percentual": 65, "preenchidas": 0}
}
vagas_preenchidas = 0
lista_espera = []

# --- Conexão com Google Sheets ---
try:
    service_account_json = st.secrets["SERVICE_ACCOUNT_JSON"]
    GCP_CREDS = json.loads(service_account_json)
    SHEETS_MANAGER = GSheetsManager(
        credenciais=GCP_CREDS,
        planilha_id="1ZOvtUy2dcMIIKG4E-aHSpxzWIZgCcRdav7jo2WWY2nk",
        worksheet_name="RespostasCV"
    )
except Exception as e:
    st.error(f"Erro ao conectar com Google Sheets: {e}")
    st.stop()

# --- Funções de validação e classificação ---
def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def extrair_texto_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

def verificar_requisitos_minimos(dados):
    try:
        data_nasc = datetime.strptime(dados["Data de nascimento"], "%d/%m/%Y")
        idade = (datetime.now() - data_nasc).days // 365
        if dados["Nível superior"] == "Sim":
            meses_restantes = (datetime.strptime(dados["Previsão de conclusão"], "%m/%Y") - datetime.now()).days // 30
            semestre_valido = int(dados["Semestre"]) >= 2
        else:
            meses_restantes = 13
            semestre_valido = True
        return (
            idade >= 18 and
            dados["Computador e internet?"] == "Sim" and
            dados["Nível de Inglês"] != "Nenhum" and
            dados["Tem interesse em CRM?"] == "Sim" and
            dados["Interesse em estagiar?"] == "Sim" and
            semestre_valido and
            (dados["Nível superior"] != "Sim" or meses_restantes >= 13_
