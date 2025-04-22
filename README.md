# Programa de Capacitação CRMAItch – Seleção Inteligente para Diversidade em CRM e IA

## Visão Geral

O **CRMAItch** é um sistema inteligente de **classificação de candidatos** para programas de capacitação com foco em CRM (Customer Relationship Management) e Inteligência Artificial. O projeto visa apoiar processos seletivos mais **inclusivos, objetivos e baseados em dados**, respeitando critérios técnicos e de diversidade.

O sistema foi desenvolvido durante o Bootcamp de LLM da SoulCode Academy, com tecnologias open-source, e está disponível como um aplicativo web interativo no Hugging Face Spaces.

[🔗 Acessar o Space](https://huggingface.co/spaces/Crislene/MAITch)

---

## Objetivos

- Automatizar o processo de avaliação de elegibilidade para programas de capacitação
- Garantir a reserva mínima de 35% das vagas para candidatos de grupos diversos
- Proporcionar uma triagem transparente, justa e auditável
- Promover a inclusão de mulheres, negros, indígenas, LGBTQIAPN+ e pessoas com deficiência

---

## Arquitetura da Solução

| Camada              | Tecnologia            | Descrição                                      |
|---------------------|------------------------|------------------------------------------------|
| Interface Web       | Gradio                 | Formulário de inscrição e retorno personalizado |
| Lógica de Negócio   | Python 3.10            | Classificação e verificação de critérios        |
| Modelo de ML        | Scikit-learn           | Classificador baseado em Árvore de Decisão     |
| Armazenamento       | Google Sheets (via gspread) | Registro automatizado dos dados           |
| Hospedagem          | Hugging Face Spaces    | Deploy do sistema em ambiente web              |

---

## Modelo de Classificação

O modelo utilizado é uma **Árvore de Decisão**, escolhida pela sua interpretabilidade e boa performance em bases estruturadas com múltiplos critérios. Foram utilizadas **20.000 entradas simuladas** com balanceamento entre ampla concorrência e diversidade.

### Algoritmo

```python
DecisionTreeClassifier(
    max_depth=5,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42
)
```

### Variáveis de Entrada

- `genero`
- `etnia`
- `lgbt`
- `pcd`
- `semestre`
- `previsao_conclusao`
- `computador`
- `disponibilidade`
- `ingles`
- `capacitacao_anterior`
- `interesse_crm`
- `interesse_estagio`

A variável alvo `resultado` define se o(a) candidato(a) será aprovado ou não.

---

## Regras de Elegibilidade

| Critério                         | Requisito                             |
|----------------------------------|----------------------------------------|
| Semestre                         | A partir do 2º                         |
| Previsão de Conclusão            | Pelo menos 13 meses até a conclusão   |
| Computador e Internet            | Obrigatório                            |
| Disponibilidade de horário       | Não pode ser eventual                 |
| Aceite para Estágio              | Obrigatório                            |

Candidatos que não cumprirem esses critérios recebem uma resposta padrão positiva, mas não avançam na seleção.

---

## Lógica de Cotas e Classificação

### Reservas:

- **35%** das vagas para grupos diversos (gênero, etnia, LGBTQIAPN+, PCD)
- **65%** para ampla concorrência

### Prioridade:

1. Elegíveis e diversos → vaga em cota
2. Elegíveis não diversos → ampla concorrência
3. Diversos sem vaga → ampla concorrência
4. Se não elegível → não aprovado

---

## Métricas de Avaliação

O modelo foi avaliado com base em uma amostra de teste com os seguintes resultados:

```text
              precision    recall  f1-score   support

           0       0.88      0.90      0.89        65
           1       0.84      0.80      0.82        35

    accuracy                           0.86       100
   macro avg       0.86      0.85      0.85       100
weighted avg       0.86      0.86      0.86       100
```

---

## Estrutura do Projeto

```
CRMAItch/
├── app.py                          # Formulário Gradio com lógica principal
├── classificador_diversidade.py   # Modelo de árvore de decisão e regras
├── gsheets.py                     # Integração com planilha Google Sheets
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação
```

---

## Como Executar

### Requisitos

- Python 3.10+
- Conta com acesso a uma planilha no Google Sheets (e credenciais configuradas)

### Instalação

```bash
git clone https://github.com/seu_usuario/CRMAItch.git
cd CRMAItch
pip install -r requirements.txt
```

### Execução local

```bash
python app.py
```

---

## Contribuição

Contribuições são bem-vindas!

1. Faça um fork
2. Crie sua branch: `git checkout -b nova-feature`
3. Faça commits claros: `git commit -m "feat: adiciona validação para campo X"`
4. Suba sua branch: `git push origin nova-feature`
5. Crie um Pull Request

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

<div align="center">  
  <p>Desenvolvido com ❤️ por <a href="https://github.com/crislenenunes">Crislene Nunes</a> durante o Bootcamp de IA LLM da SoulCode</p>  
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">  
  <img src="https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn" alt="Scikit-learn">  
  <img src="https://img.shields.io/badge/Gradio-4.28.3-green?logo=gradio" alt="Gradio">  
</div>
```
