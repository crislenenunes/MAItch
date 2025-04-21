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
            (dados["Nível superior"] != "Sim" or meses_restantes >= 13)
        )
    except:
        return False

def classificar_vaga(dados):
    global vagas_preenchidas, lista_espera

    if not verificar_requisitos_minimos(dados):
        return "NÃO APTO", "Não atende aos requisitos mínimos"

    for cota, config in COTAS.items():
        if cota != "AMPLA" and config["critério"](dados) and COTAS[cota]["preenchidas"] < int(VAGAS_TOTAIS * config["percentual"] / 100):
            COTAS[cota]["preenchidas"] += 1
            vagas_preenchidas += 1
            return "APTO", f"Cota {cota}"

    if vagas_preenchidas < VAGAS_TOTAIS:
        COTAS["AMPLA"]["preenchidas"] += 1
        vagas_preenchidas += 1
        return "APTO", "Ampla concorrência"

    if len(lista_espera) < (LISTA_ESPERA_MAX - VAGAS_TOTAIS):
        posicao = len(lista_espera) + 1
        lista_espera.append(dados["E-mail"])
        return "LISTA_ESPERA", f"Posição {posicao}"

    return "NÃO APTO", "Vagas esgotadas"

# --- Interface Streamlit ---
st.title("📋 Formulário de Candidatura - Programa de Capacitação")

with st.form("formulario"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    telefone = st.text_input("Telefone")
    nascimento = st.text_input("Data de nascimento (DD/MM/AAAA)")

    genero = st.selectbox("Gênero", ["", "Feminino", "Masculino", "Não binário"])
    etnia = st.selectbox("Etnia", ["", "Branca", "Preta", "Parda", "Indígena", "Amarela"])
    lgbt = st.selectbox("Você se identifica como LGBTQIAPN+?", ["", "Sim", "Não"])
    pcd = st.selectbox("Você é PCD?", ["", "Sim", "Não"])
    if pcd == "Sim":
        tipo_deficiencia = st.text_input("Qual tipo de deficiência?")
        acessibilidade = st.text_input("Precisa de alguma acessibilidade?")
    else:
        tipo_deficiencia = ""
        acessibilidade = ""

    cursando = st.selectbox("Está cursando nível superior?", ["", "Sim", "Não"])
    if cursando == "Sim":
        curso = st.text_input("Curso")
        instituicao = st.text_input("Instituição")
        semestre = st.text_input("Semestre atual")
        previsao = st.text_input("Previsão de conclusão (MM/AAAA)")
    else:
        curso = instituicao = semestre = previsao = ""

    computador = st.selectbox("Você possui computador e acesso à internet?", ["", "Sim", "Não"])
    disponibilidade = st.selectbox("Disponibilidade de horário", ["", "Integral", "Parcial", "Eventual"])
    ingles = st.selectbox("Nível de Inglês", ["", "Nenhum", "Básico", "Intermediário", "Avançado"])
    capacitacao_anterior = st.selectbox("Já participou de outras capacitações?", ["", "Sim", "Não"])
    interesse_crm = st.selectbox("Tem interesse em CRM?", ["", "Sim", "Não"])
    interesse_estagio = st.selectbox("Interesse em estagiar?", ["", "Sim", "Não"])

    cv_pdf = st.file_uploader("Anexe seu currículo em PDF", type=["pdf"])

    submit = st.form_submit_button("Enviar inscrição")

if submit:
    if not all([nome, email, telefone, nascimento, genero, etnia, lgbt, pcd, computador,
                disponibilidade, ingles, interesse_crm, interesse_estagio]):
        st.warning("⚠️ Preencha todos os campos obrigatórios.")
    elif not validar_email(email):
        st.warning("⚠️ E-mail inválido.")
    else:
        cv_text = extrair_texto_pdf(cv_pdf) if cv_pdf else ""

        dados = {
            "Nome": nome,
            "E-mail": email,
            "Telefone": telefone,
            "Data de nascimento": nascimento,
            "Gênero": genero,
            "Etnia": etnia,
            "LGBTQIA+": lgbt,
            "PCD": pcd,
            "Tipo de deficiência": tipo_deficiencia,
            "Acessibilidade": acessibilidade,
            "Nível superior": cursando,
            "Semestre": semestre,
            "Curso": curso,
            "Instituição": instituicao,
            "Previsão de conclusão": previsao,
            "Computador e internet?": computador,
            "Disponibilidade": disponibilidade,
            "Nível de Inglês": ingles,
            "Já fez outras capacitações?": capacitacao_anterior,
            "Tem interesse em CRM?": interesse_crm,
            "Interesse em estagiar?": interesse_estagio,
            "Texto do CV": cv_text,
            "Data de inscrição": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        resultado, info = classificar_vaga(dados)
        dados["Resultado"] = resultado

        if resultado == "APTO" or resultado == "LISTA_ESPERA":
            SHEETS_MANAGER.enviar_resposta(dados)
            if resultado == "APTO":
                st.success(f"✅ Inscrição registrada com sucesso! ({info})")
            else:
                st.info(f"🟡 Você foi incluído na lista de espera ({info})")
        else:
            st.warning("⚠️ Obrigado pelo interesse! Sua inscrição foi registrada, mas os requisitos mínimos não foram atendidos.")
