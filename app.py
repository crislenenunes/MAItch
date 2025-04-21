import streamlit as st
import json
from gsheets import GSheetsManager
from datetime import datetime

# Inicialização do estado da sessão
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Função de classificação da vaga
def classificar_vaga(dados):
    if dados.get("PCD") == "Sim":
        return "Aprovado - PCD", "Candidato com deficiência aprovado"
    else:
        return "Aprovado", "Candidato aprovado para ampla concorrência"

# --- Conexão com Google Sheets ---
try:
    service_account_json = st.secrets["SERVICE_ACCOUNT_JSON"]
    GCP_CREDS = json.loads(service_account_json)
    
    SHEETS_MANAGER = GSheetsManager(
        credenciais=GCP_CREDS,
        planilha_id="1ZOvtUy2dcMIIKG4E-aHSpxzWIZgCcRdav7jo2WWY2nk",
        worksheet_name="RespostasCV"
    )
    st.success("Conexão com Google Sheets estabelecida com sucesso!")
except Exception as e:
    st.error(f"Erro ao conectar com Google Sheets: {e}")
    st.stop()

# Formulário de inscrição
st.title("Formulário de Inscrição")
with st.form(key='inscricao_form'):
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    telefone = st.text_input("Telefone")
    data_nascimento = st.date_input("Data de Nascimento")
    genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
    etnia = st.selectbox("Etnia", ["Branco", "Negro", "Pardo", "Indígena", "Outro"])
    pcd = st.selectbox("Você é PCD?", ["Sim", "Não"])
    interesse_crm = st.checkbox("Tenho interesse em CRM")
    interesse_estagio = st.checkbox("Tenho interesse em Estágio")
    
    submitted = st.form_submit_button("Enviar Inscrição")

# Processamento do formulário
if submitted or st.session_state.form_submitted:
    st.session_state.form_submitted = True
    
    dados = {
        "Nome": nome,
        "E-mail": email,
        "Telefone": telefone,
        "Data de Nascimento": str(data_nascimento),
        "Gênero": genero,
        "Etnia": etnia,
        "LGBT": "Não",
        "PCD": pcd,
        "Cursando": "Sim",
        "Semestre": 3,
        "Curso": "Curso de Exemplo",
        "Instituição": "Instituição de Exemplo",
        "Previsão de Conclusão": "2026",
        "Computador": "Sim",
        "Disponibilidade": "Sim",
        "Inglês": "Intermediário",
        "Capacitação Anterior": "Não",
        "Interesse CRM": interesse_crm,
        "Interesse Estágio": interesse_estagio,
    }

    try:
        resultado_classificacao, detalhes_classificacao = classificar_vaga(dados)
        dados["Resultado"] = resultado_classificacao
        SHEETS_MANAGER.registrar_candidatura(dados)
        st.success(f"Inscrição enviada com sucesso! {detalhes_classificacao}")
        
        # Opção para novo cadastro
        if st.button("Fazer nova inscrição"):
            st.session_state.form_submitted = False
            st.experimental_rerun()
            
    except Exception as e:
        st.error(f"Erro ao enviar inscrição: {e}")
        st.session_state.form_submitted = False
