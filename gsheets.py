import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class GSheetsManager:
    def __init__(self, credenciais, planilha_id, worksheet_name):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        try:
            creds = Credentials.from_service_account_info(credenciais, scopes=self.scope)
            self.client = gspread.authorize(creds)
            print("Autenticação bem-sucedida")
        except Exception as e:
            raise Exception(f"Erro na autenticação do Google Sheets: {e}")
        
        try:
            self.planilha = self.client.open_by_key(planilha_id)
            self.worksheet = self.planilha.worksheet(worksheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            raise Exception(f"Planilha com ID {planilha_id} não encontrada.")
        except gspread.exceptions.WorksheetNotFound:
            raise Exception(f"Aba {worksheet_name} não encontrada na planilha.")
        
        # Verificar se a aba tem cabeçalhos e se não tiver, adicioná-los
        if len(self.worksheet.get_all_values()) < 1:
            self.worksheet.append_row([
                "Nome", "E-mail", "Telefone", "Data de Nascimento", "Gênero", "Etnia", 
                "LGBT", "PCD", "Cursando", "Semestre", "Curso", "Instituição", 
                "Previsão de Conclusão", "Computador", "Disponibilidade", "Inglês", 
                "Capacitação Anterior", "Interesse CRM", "Interesse Estágio", 
                "Resultado", "Data Registro"
            ])

    def registrar_candidatura(self, dados):
        dados["Data Registro"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        row_data = [
            dados.get("Nome", ""),
            dados.get("E-mail", ""),
            dados.get("Telefone", ""),
            dados.get("Data de Nascimento", ""),
            dados.get("Gênero", ""),
            dados.get("Etnia", ""),
            dados.get("LGBT", ""),
            dados.get("PCD", ""),
            dados.get("Cursando", ""),
            str(dados.get("Semestre", "")),  # Convertendo para string para evitar erros
            dados.get("Curso", ""),
            dados.get("Instituição", ""),
            dados.get("Previsão de Conclusão", ""),
            dados.get("Computador", ""),
            dados.get("Disponibilidade", ""),
            dados.get("Inglês", ""),
            dados.get("Capacitação Anterior", ""),
            "Sim" if dados.get("Interesse CRM", False) else "Não",
            "Sim" if dados.get("Interesse Estágio", False) else "Não",
            dados.get("Resultado", ""),  # Resultado da classificação
            dados["Data Registro"]
        ]
        
        try:
            self.worksheet.append_row(row_data)
            print(f"Dados adicionados com sucesso: {row_data}")
            return True
        except Exception as e:
            raise Exception(f"Erro ao adicionar dados na planilha: {e}")

