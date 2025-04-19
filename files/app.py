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

# --- Helper Functions ---
def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def validar_candidatura(nome, email, telefone, nascimento, cursando, semestre, curso, instituicao, previsao,
                       computador, disponibilidade, ingles, capacitacao_anterior, interesse_crm, interesse_estagio):
    erros = []
    if not nome:
        erros.append("Nome é obrigatório.")
    if not validar_email(email):
        erros.append("E-mail inválido.")
    if not telefone:
        erros.append("Telefone é obrigatório.")
    if not nascimento:
        erros.append("Data de nascimento é obrigatória.")
    if cursando == "Sim":
        if not curso:
            erros.append("Informe o curso.")
        if not instituicao:
            erros.append("Informe a instituição.")
        if not semestre:
            erros.append("Informe o semestre.")
    if not computador:
        erros.append("Informe se possui computador.")
    if not disponibilidade:
        erros.append("Informe sua disponibilidade.")
    if interesse_estagio not in ["Sim", "Não"] or interesse_crm not in ["Sim", "Não"]:
        erros.append("Responda sobre interesse em CRM e estágio.")
    return erros

def classificar_vaga(dados):
    global vagas_preenchidas, lista_espera
    
    for cota, config in COTAS.items():
        if cota != "AMPLA" and config["critério"](dados) and COTAS[cota]["preenchidas"] < int(VAGAS_TOTAIS * (config["percentual"]/100)):
            COTAS[cota]["preenchidas"] += 1
            vagas_preenchidas += 1
            return "APTO", None
    
    if vagas_preenchidas < VAGAS_TOTAIS:
        COTAS["AMPLA"]["preenchidas"] += 1
        vagas_preenchidas += 1
        return "APTO", None
    
    if len(lista_espera) < (LISTA_ESPERA_MAX - VAGAS_TOTAIS):
        posicao = len(lista_espera) + 1
        lista_espera.append(dados["E-mail"])
        return "LISTA_ESPERA", posicao
    
    return "NÃO APTO", None

def analisar_clusters():
    if not ML_ENABLED:
        print("Cluster analysis disabled - scikit-learn not available")
        return None
    
    try:
        dados = SHEETS_MANAGER.worksheet.get_all_records()
        if len(dados) < 5:
            return None
            
        df = pd.DataFrame(dados)
        features = pd.get_dummies(df[['Semestre', 'Inglês', 'Gênero', 'Etnia', 'PCD']])
        
        scaler = StandardScaler()
        dados_escalados = scaler.fit_transform(features)
        
        pca = PCA(n_components=2)
        dados_reduzidos = pca.fit_transform(dados_escalados)
        
        kmeans = KMeans(n_clusters=min(5, len(dados)-1), random_state=42)
        clusters = kmeans.fit_predict(dados_reduzidos)
        
        return clusters
    except Exception as e:
        print(f"Cluster analysis error: {e}")
        return None


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

# --- Main Processing Function ---
def processar_candidatura(nome, email, telefone, nascimento,
                         genero, etnia, lgbt, pcd,
                         cursando, semestre, curso, instituicao, previsao,
                         computador, disponibilidade, ingles, capacitacao_anterior,
                         interesse_crm, interesse_estagio,
                         cv_text, cv_pdf):
    
    erros = validar_candidatura(nome, email, telefone, nascimento, cursando, semestre, 
                               curso, instituicao, previsao, computador, disponibilidade,
                               ingles, capacitacao_anterior, interesse_crm, interesse_estagio)
    
    if erros:
        return f"""
        <div style='background:#ffebee; padding:20px; border-radius:10px;'>
            <h3>❌ Dados incompletos</h3>
            <ul>{''.join([f'<li>{e}</li>' for e in erros])}</ul>
        </div>
        """

    if cv_pdf is not None:
        try:
            cv_texto = extract_text_from_pdf(cv_pdf)
        except Exception as e:
            return f"""
            <div style='background:#ffebee; padding:20px; border-radius:10px;'>
                <h3>❌ Erro ao ler PDF</h3>
                <p>{str(e)}</p>
            </div>
            """
    else:
        cv_texto = cv_text or ""

    dados = {
        "Nome": nome,
        "E-mail": email,
        "Telefone": telefone,
        "Data de Nascimento": nascimento,
        "Gênero": genero,
        "Etnia": etnia,
        "LGBT": lgbt,
        "PCD": pcd,
        "Cursando": cursando,
        "Semestre": semestre,
        "Curso": curso,
        "Instituição": instituicao,
        "Previsão de Conclusão": previsao,
        "Computador": computador,
        "Disponibilidade": disponibilidade,
        "Inglês": ingles,
        "Capacitação Anterior": capacitacao_anterior,
        "Interesse CRM": interesse_crm,
        "Interesse Estágio": interesse_estagio,
        "Currículo": cv_texto[:500] + ("..." if len(cv_texto) > 500 else "")
    }

    status, posicao = classificar_vaga(dados)
    
    if status == "APTO":
        texto_resultado = "APTO - Pré-aprovado"
    elif status == "LISTA_ESPERA":
        texto_resultado = f"LISTA DE ESPERA (Posição {posicao})"
    else:
        texto_resultado = "NÃO APTO - Vagas esgotadas"
    
    dados["Resultado"] = texto_resultado
    dados["Data Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        SHEETS_MANAGER.registrar_candidatura(dados)
        
        if status == "APTO":
            return f"""
            <div style='background:#e8f5e9; padding:20px; border-radius:10px;'>
                <h3>🎉 Parabéns, {nome.split()[0]}!</h3>
                <p>Sua candidatura foi <strong>pré-aprovada</strong> para o Programa de Capacitação em CRM!</p>
                <p>Status: {texto_resultado}</p>
                <h4>📅 Próximos passos:</h4>
                <ol>
                    <li>Você receberá um e-mail em <strong>{email}</strong> em até 3 dias úteis</li>
                    <li>Teste online de conhecimentos gerais</li>
                    <li>Dinâmica de grupo virtual</li>
                    <li>Entrevista individual</li>
                </ol>
            </div>
            """
        elif status == "LISTA_ESPERA":
            return f"""
            <div style='background:#fff3e0; padding:20px; border-radius:10px;'>
                <h3>⏳ Você está na lista de espera!</h3>
                <p>Sua candidatura está na <strong>posição {posicao}</strong> da lista.</p>
                <p>Status: {texto_resultado}</p>
                <p>Entraremos em contato caso novas vagas se abram.</p>
            </div>
            """
        else:
            return f"""
            <div style='background:#ffebee; padding:20px; border-radius:10px;'>
                <h3>⚠️ Vagas esgotadas</h3>
                <p>Status: {texto_resultado}</p>
                <p>Todas as vagas foram preenchidas. Fique atento às próximas turmas!</p>
            </div>
            """
    except Exception as e:
        print(f"Erro ao salvar: {str(e)}")
        return f"""
        <div style='background:#ffebee; padding:20px; border-radius:10px;'>
            <h3>❌ Erro no processamento</h3>
            <p>Ocorreu um erro ao registrar sua candidatura: {str(e)}</p>
        </div>
        """

# --- Gradio Interface ---
with gr.Blocks(title="🚀 Programa de Capacitação CRMatch – Inscreva-se", css="""
    .gradio-container {max-width: 800px !important}
    .gr-input {background-color: #f9f9f9 !important}
""") as app:
    
    gr.Markdown("## 🚀 Programa de Capacitação CRMatch – Inscreva-se!")
    gr.Markdown("Preencha todos os campos obrigatórios (*) para se candidatar ao nosso programa.")

    with gr.Row():
        nome = gr.Textbox(label="Nome completo*", placeholder="Ex: Maria da Silva Oliveira")
        email = gr.Textbox(label="E-mail*", placeholder="seu@email.com")
    
    with gr.Row():
        telefone = gr.Textbox(label="Telefone*", placeholder="+55 11 99999-9999")
        nascimento = gr.Textbox(label="Data de Nascimento*", placeholder="DD/MM/AAAA")

    with gr.Row():
        genero = gr.Radio(label="Gênero*", choices=["Masculino", "Feminino", "Não Binário", "Prefiro não dizer"])
        etnia = gr.Radio(label="Etnia*", choices=["Branca", "Preta", "Parda", "Indígena", "Amarela", "Prefiro não dizer"])

    with gr.Row():
        lgbt = gr.Radio(label="Você faz parte da comunidade LGBTQIAPN+?*", choices=["Sim", "Não", "Prefiro não dizer"])
        pcd = gr.Radio(label="Você é Pessoa com Deficiência?*", choices=["Sim", "Não", "Prefiro não dizer"])
    
    with gr.Row():
        pcd_tipo = gr.Dropdown(
            label="Tipo de deficiência", 
            choices=["Física", "Visual", "Auditiva", "Intelectual", "Neurodiversa", "Outra"], 
            visible=False,
            interactive=True
        )
        pcd_acessibilidade = gr.Textbox(
            label="Necessidades de acessibilidade", 
            placeholder="Descreva adaptações necessárias...", 
            visible=False,
            interactive=True
        )

    def toggle_pcd_fields(pcd_resposta):
        visible = pcd_resposta == "Sim"
        return (
            gr.update(visible=visible),  # Tipo de deficiência
            gr.update(visible=visible)   # Acessibilidade
        )

    pcd.change(
        fn=toggle_pcd_fields,
        inputs=pcd,
        outputs=[pcd_tipo, pcd_acessibilidade]
    )

    with gr.Row():
        cursando = gr.Radio(label="Você está cursando o ensino superior?*", choices=["Sim", "Não"])
        semestre = gr.Dropdown(label="Semestre atual*", choices=[str(i) for i in range(1, 11)])

    with gr.Row():
        curso = gr.Textbox(label="Curso*", placeholder="Ex: Administração")
        instituicao = gr.Textbox(label="Instituição*", placeholder="Ex: Universidade de São Paulo")

    previsao = gr.Textbox(label="Previsão de Conclusão*", placeholder="MM/AAAA")

    with gr.Row():
        computador = gr.Radio(label="Você possui computador/notebook com acesso a internet?*", choices=["Sim", "Não"])
        disponibilidade = gr.Radio(label="Disponibilidade de horário*", choices=["Manhã", "Tarde", "Noite", "Integral"])

    ingles = gr.Radio(label="Nível de inglês*", choices=["Nenhum", "Básico", "Intermediário", "Avançado", "Fluente"])

    with gr.Row():
        capacitacao_anterior = gr.Radio(label="Já participou de algum programa de capacitação da CRMatch?*", choices=["Sim", "Não"])
        interesse_crm = gr.Radio(label="Tem interesse em trabalhar com CRM num futuro próximo?*", choices=["Sim", "Não"])
        interesse_estagio = gr.Radio(label="Tem interesse em estágio ao final da formação?*", choices=["Sim", "Não"])

    cv_text = gr.Textbox(label="Cole seu currículo aqui*", lines=4, placeholder="Descreva suas experiências profissionais...")
    cv_pdf = gr.File(label="Ou envie em PDF (opcional)", file_types=[".pdf"], type="filepath")

    resultado = gr.HTML()
    btn = gr.Button("Enviar candidatura", variant="primary")

    # Configuração do botão com limpeza automática
    btn.click(
        fn=processar_candidatura,
        inputs=[nome, email, telefone, nascimento,
                genero, etnia, lgbt, pcd,
                cursando, semestre, curso, instituicao, previsao,
                computador, disponibilidade, ingles, capacitacao_anterior,
                interesse_crm, interesse_estagio,
                cv_text, cv_pdf],
        outputs=resultado
    ).then(
        fn=limpar_formulario,
        outputs=[nome, email, telefone, nascimento,
                 genero, etnia, lgbt, pcd,
                 cursando, semestre, curso, instituicao, previsao,
                 computador, disponibilidade, ingles, capacitacao_anterior,
                 interesse_crm, interesse_estagio,
                 cv_text, cv_pdf]
    )

app.launch()
