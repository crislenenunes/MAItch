import gradio as gr
import re
import json
import PyPDF2
import pandas as pd
import os
from gsheets import GSheetsManager
from datetime import datetime
from google.oauth2 import service_account

try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    ML_ENABLED = True
except ImportError:
    print("Warning: scikit-learn not available. Cluster analysis disabled.")
    ML_ENABLED = False

VAGAS_TOTAIS = 50
LISTA_ESPERA_MAX = 63  # 50 + 25%
COTAS = {
    "PCD": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("PCD", "")).upper() == "SIM"},
    "RAÇA": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("Etnia", "")).upper() in ["PRETA", "PARDA", "INDÍGENA"]},
    "GÊNERO": {"percentual": 10, "preenchidas": 0, "critério": lambda d: str(d.get("Gênero", "")).upper() in ["FEMININO", "NÃO BINÁRIO", "NAO BINARIO"]},
    "LGBTQIA+": {"percentual": 5, "preenchidas": 0, "critério": lambda d: str(d.get("LGBT", "")).upper() == "SIM"},
    "AMPLA": {"percentual": 65, "preenchidas": 0}
}

vagas_preenchidas = 0
lista_espera = []

try:
    service_account_json = os.getenv("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("Variável SERVICE_ACCOUNT_JSON não encontrada nas Secrets")

    GCP_CREDS = json.loads(service_account_json)
    
    SHEETS_MANAGER = GSheetsManager(
        credenciais=GCP_CREDS,
        planilha_id="1ZOvtUy2dcMIIKG4E-aHSpxzWIZgCcRdav7jo2WWY2nk",
        worksheet_name="RespostasCV"
    )
    print("Conexão com Google Sheets configurada com sucesso!")

except Exception as e:
    print(f"Erro crítico na configuração do Google Sheets: {str(e)}")
    raise

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def validar_candidatura(nome, email, telefone, nascimento, genero, etnia, lgbt, pcd,
                       cursando, semestre, curso, instituicao, previsao,
                       computador, disponibilidade, ingles, capacitacao_anterior, 
                       interesse_crm, interesse_estagio):
    erros = []
    
    # Validações básicas (dados obrigatórios para todos)
    if not nome: erros.append("Nome é obrigatório.")
    if not validar_email(email): erros.append("E-mail inválido.")
    if not telefone: erros.append("Telefone é obrigatório.")
    if not genero: erros.append("Gênero é obrigatório.")
    if not etnia: erros.append("Etnia é obrigatória.")
    if not lgbt: erros.append("Informação sobre LGBTQIA+ é obrigatória.")
    if not pcd: erros.append("Informação sobre PCD é obrigatória.")
    if not cursando: erros.append("Informe se está cursando faculdade.")
    if not computador: erros.append("Informe se possui computador.")
    if not disponibilidade: erros.append("Informe sua disponibilidade.")
    if not ingles: erros.append("Informe seu nível de inglês.")
    if interesse_crm not in ["Sim", "Não"]: erros.append("Informe interesse em CRM.")
    if interesse_estagio not in ["Sim", "Não"]: erros.append("Informe interesse em estágio.")
    
    # Validação de formato de dados básicos
    try:
        datetime.strptime(nascimento, "%d/%m/%Y")
    except:
        erros.append("Data de nascimento inválida (use DD/MM/AAAA).")
    
    # Validações específicas para quem está cursando
    if cursando == "Sim":
        if not curso: erros.append("Informe o curso.")
        if not instituicao: erros.append("Informe a instituição.")
        if not semestre: erros.append("Informe o semestre.")
        try:
            int(semestre)  # Apenas verifica se é número válido
        except:
            erros.append("Semestre inválido.")
        
        if not previsao: erros.append("Informe a previsão de conclusão.")
        try:
            datetime.strptime(previsao, "%m/%Y")
        except:
            erros.append("Previsão de conclusão inválida (use MM/AAAA).")
    
    return erros

def verificar_requisitos_minimos(dados):
    try:
        data_nasc = datetime.strptime(dados["Data de Nascimento"], "%d/%m/%Y")
        idade = (datetime.now() - data_nasc).days // 365
        
        # Verificação condicional para quem está cursando
        if dados["Cursando"] == "Sim":
            meses_restantes = (datetime.strptime(dados["Previsão de Conclusão"], "%m/%Y") - datetime.now()).days // 30
            semestre_valido = int(dados["Semestre"]) >= 2
        else:
            meses_restantes = 13  # Assume válido se não está cursando
            semestre_valido = True  # Não aplicável
        
        return (
            idade >= 18 and
            dados["Computador"] == "Sim" and
            dados["Inglês"] != "Nenhum" and
            dados["Interesse CRM"] == "Sim" and
            dados["Interesse Estágio"] == "Sim" and
            semestre_valido and
            (dados["Cursando"] != "Sim" or meses_restantes >= 13)
        )
    except:
        return False

def classificar_vaga(dados):
    global vagas_preenchidas, lista_espera
    
    # Verifica requisitos mínimos
    if not verificar_requisitos_minimos(dados):
        return "NÃO APTO", "Não atende aos requisitos mínimos"
    
    # Verifica cotas primeiro
    for cota, config in COTAS.items():
        if cota != "AMPLA" and config["critério"](dados) and COTAS[cota]["preenchidas"] < int(VAGAS_TOTAIS * (config["percentual"]/100)):
            COTAS[cota]["preenchidas"] += 1
            vagas_preenchidas += 1
            return "APTO", f"Cota {cota}"
    
    # Vagas de ampla concorrência
    if vagas_preenchidas < VAGAS_TOTAIS:
        COTAS["AMPLA"]["preenchidas"] += 1
        vagas_preenchidas += 1
        return "APTO", "Ampla concorrência"
    
    # Lista de espera
    if len(lista_espera) < (LISTA_ESPERA_MAX - VAGAS_TOTAIS):
        posicao = len(lista_espera) + 1
        lista_espera.append(dados["E-mail"])
        return "LISTA_ESPERA", posicao
    
    return "NÃO APTO", "Vagas esgotadas"

def limpar_formulario():
    return [
        "",    # nome
        "",    # email
        "",    # telefone
        "",    # nascimento
        None,  # genero
        None,  # etnia
        None,  # lgbt
        None,  # pcd
        None,  # cursando
        None,  # semestre
        "",    # curso
        "",    # instituicao
        "",    # previsao
        None,  # computador
        None,  # disponibilidade
        None,  # ingles
        None,  # capacitacao_anterior
        None,  # interesse_crm
        None,  # interesse_estagio
        "",    # cv_text
        None   # cv_pdf
    ]

def processar_candidatura(nome, email, telefone, nascimento,
                         genero, etnia, lgbt, pcd,
                         cursando, semestre, curso, instituicao, previsao,
                         computador, disponibilidade, ingles, capacitacao_anterior,
                         interesse_crm, interesse_estagio,
                         cv_text, cv_pdf):
    
    erros = validar_candidatura(nome, email, telefone, nascimento, genero, etnia, lgb
