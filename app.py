import streamlit as st
import json
from gsheets import GSheetsManager
from datetime import datetime
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Função de classificação da vaga (simulada para fins de exemplo)
def classificar_vaga(dados):
    # Aqui você pode incluir a lógica de classificação com base nas informações do candidato
    if dados.get("PCD") == "Sim":
        return "Aprovado - PCD", "Candidato com deficiência aprovado"
    else:
        return "Aprovado", "Candidato aprovado para ampla concorrência"

# --- Conexão com Google Sheets ---
try:
    # Carregar credenciais do Google Sheets
    service_account_json = st.secrets["SERVICE_ACCOUNT_JSON"]
    GCP_CREDS = json.loads(service_account_json)
    
    # Criando a instância de GSheetsManager
    SHEETS_MANAGER = GSheetsManager(
        credenciais=GCP_CREDS,
        planilha_id="1ZOvtUy2dcMIIKG4E-aHSpxzWIZgCcRdav7jo2WWY2nk",  # Use seu ID correto
        worksheet_name="RespostasCV"  # Use o nome correto da aba
    )
    
    st.success("Conexão com Google Sheets estabelecida com sucesso!")
except Exception as e:
    st.error(f"Erro ao conectar com Google Sheets: {e}")
    st.stop()

# Formulário de inscrição (exemplo simples)
st.title("Formulário de Inscrição")
nome = st.text_input("Nome")
email = st.text_input("E-mail")
telefone = st.text_input("Telefone")
data_nascimento = st.date_input("Data de Nascimento")
genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
etnia = st.selectbox("Etnia", ["Branco", "Negro", "Pardo", "Indígena", "Outro"])
pcd = st.selectbox("Você é PCD?", ["Sim", "Não"])

# Condições adicionais baseadas nas respostas
interesse_crm = st.checkbox("Tenho interesse em CRM")
interesse_estagio = st.checkbox("Tenho interesse em Estágio")

# Registrar candidatura
if st.button("Enviar Inscrição"):
    dados = {
        "Nome": nome,
        "E-mail": email,
        "Telefone": telefone,
        "Data de Nascimento": str(data_nascimento),
        "Gênero": genero,
        "Etnia": etnia,
        "LGBT": "Não",
        "PCD": pcd,
        "Cursando": "Sim",  # Exemplo fixo
        "Semestre": 3,  # Exemplo fixo
        "Curso": "Curso de Exemplo",  # Exemplo fixo
        "Instituição": "Instituição de Exemplo",  # Exemplo fixo
        "Previsão de Conclusão": "2026",  # Exemplo fixo
        "Computador": "Sim",  # Exemplo fixo
        "Disponibilidade": "Sim",  # Exemplo fixo
        "Inglês": "Intermediário",  # Exemplo fixo
        "Capacitação Anterior": "Não",  # Exemplo fixo
        "Interesse CRM": interesse_crm,
        "Interesse Estágio": interesse_estagio,
    }

    if st.button("Enviar Inscrição") or st.session_state.form_submitted:
    st.session_state.form_submitted = True
    
    try:
        resultado_classificacao, detalhes_classificacao = classificar_vaga(dados)
        dados["Resultado"] = resultado_classificacao
        
        # Registrar dados na planilha do Google Sheets
        SHEETS_MANAGER.registrar_candidatura(dados)
        
        st.success(f"Inscrição enviada com sucesso! {detalhes_classificacao}")
    except Exception as e:
        st.error(f"Erro ao enviar inscrição: {e}")
