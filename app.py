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

def processar_candidatura(nome, email, telefone, nascimento,
                         genero, etnia, lgbt, pcd,
                         cursando, semestre, curso, instituicao, previsao,
                         computador, disponibilidade, ingles, capacitacao_anterior,
                         interesse_crm, interesse_estagio,
                         cv_text, cv_pdf):
    
    erros = validar_candidatura(nome, email, telefone, nascimento, genero, etnia, lgbt, pcd,
                              cursando, semestre, curso, instituicao, previsao,
                              computador, disponibilidade, ingles, capacitacao_anterior,
                              interesse_crm, interesse_estagio)
    
    if erros:
        return f"""
        <div style='background:#ffebee; padding:20px; border-radius:10px;'>
            <h3>❌ Dados incompletos ou inválidos</h3>
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
        "Semestre": semestre if cursando == "Sim" else "",
        "Curso": curso if cursando == "Sim" else "",
        "Instituição": instituicao if cursando == "Sim" else "",
        "Previsão de Conclusão": previsao if cursando == "Sim" else "",
        "Computador": computador,
        "Disponibilidade": disponibilidade,
        "Inglês": ingles,
        "Capacitação Anterior": capacitacao_anterior,
        "Interesse CRM": interesse_crm,
        "Interesse Estágio": interesse_estagio,
        "Currículo": cv_texto[:500] + ("..." if len(cv_texto) > 500 else "")
    }

    status, detalhe = classificar_vaga(dados)
    
    dados["Resultado"] = f"{status} - {detalhe}"
    dados["Data Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        SHEETS_MANAGER.registrar_candidatura(dados)
        
        if status == "APTO":
            return f"""
            <div style='background:#e8f5e9; padding:20px; border-radius:10px;'>
                <h3>🎉 Parabéns, {nome.split()[0]}!</h3>
                <p>Sua candidatura foi <strong>pré-aprovada</strong> para o Programa de Capacitação em CRM!</p>
                <p>Status: {status} - {detalhe}</p>
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
                <p>Sua candidatura está na <strong>posição {detalhe}</strong> da lista.</p>
                <p>Status: {status}</p>
                <p>Entraremos em contato caso novas vagas se abram.</p>
            </div>
            """
        else:
            return f"""
            <div style='background:#ffebee; padding:20px; border-radius:10px;'>
                <h3>⚠️ {detalhe}</h3>
                <p>Status: {status}</p>
                <p>Infelizmente sua candidatura não atendeu aos requisitos do programa.</p>
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
        nascimento = gr.Textbox(label="Data de Nascimento* (DD/MM/AAAA)", placeholder="Ex: 15/05/2000")

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
        semestre = gr.Dropdown(label="Semestre atual", choices=[str(i) for i in range(1, 11)], visible=False)

    with gr.Row():
        curso = gr.Textbox(label="Curso", placeholder="Ex: Administração", visible=False)
        instituicao = gr.Textbox(label="Instituição", placeholder="Ex: Universidade de São Paulo", visible=False)

    previsao = gr.Textbox(label="Previsão de Conclusão", placeholder="MM/AAAA", visible=False)

    def toggle_campos_faculdade(cursando):
        visible = cursando == "Sim"
        return [
            gr.update(visible=visible),  # semestre
            gr.update(visible=visible),  # curso
            gr.update(visible=visible),  # instituicao
            gr.update(visible=visible)   # previsao
        ]

    cursando.change(
        fn=toggle_campos_faculdade,
        inputs=cursando,
        outputs=[semestre, curso, instituicao, previsao]
    )

    with gr.Row():
        computador = gr.Radio(label="Você possui computador/notebook com acesso a internet?*", choices=["Sim", "Não"])
        disponibilidade = gr.Radio(label="Disponibilidade de horário*", choices=["Manhã (8h-12h)", "Tarde (13h-17h)", "Noite (18h-22h)", "Integral"])

    ingles = gr.Radio(label="Nível de inglês*", 
                     choices=["Nenhum", "Básico", "Intermediário", "Avançado", "Fluente"],
                     info="Mínimo básico necessário")

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
