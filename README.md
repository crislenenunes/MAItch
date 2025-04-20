# Programa de Capacitação CRMatch

Este repositório apresenta o sistema completo de inscrição, avaliação e classificação de candidatos do Programa de Capacitação CRMatch. Desenvolvido com foco em diversidade, inclusão e transformação social, o projeto integra tecnologias modernas como Gradio, Google Sheets e algoritmos de aprendizado de máquina para garantir a equidade na seleção de talentos nas áreas de CRM e Inteligência Artificial.

> Acesse o projeto no Hugging Face: [https://huggingface.co/spaces/Crislene/MAITch]

---

## Visão Geral

O Programa de Capacitação CRMatch tem como propósito central democratizar o acesso ao conhecimento e às oportunidades profissionais em tecnologia. A iniciativa visa incluir grupos historicamente sub-representados no mercado de trabalho, promovendo capacitação técnica aliada à prática profissional, especialmente nas áreas de Customer Relationship Management (CRM) e Inteligência Artificial.

Grupos prioritários incluem:
- Mulheres;
- Pessoas negras, pardas e indígenas;
- Pessoas com deficiência (PCD), incluindo neurodiversas;
- Pessoas LGBTQIA+.

O projeto adota um processo de seleção estruturado em critérios objetivos, garantindo tanto a diversidade quanto a aderência aos requisitos da capacitação e estágio. O sistema automatiza desde a inscrição até a classificação, respeitando um modelo híbrido de cotas e ampla concorrência.

---

## Funcionalidades

### 1. Sistema de Cotas Integrado

O sistema de cotas implementado assegura uma distribuição justa e proporcional das vagas. A lógica de classificação reserva as seguintes proporções:

- **10%**: Pessoas com deficiência (PCD), com atenção especial à neurodiversidade;
- **10%**: Pessoas negras, pardas e indígenas;
- **10%**: Mulheres e pessoas não binárias;
- **5%**: Pessoas LGBTQIA+;
- **65%**: Ampla concorrência (candidatos que atendem aos critérios técnicos, sem estar em grupos de cota).

Candidatos podem ser classificados em mais de um critério de diversidade, mas a priorização obedece a uma ordem lógica de preenchimento. Ao atingir o limite de vagas de cada grupo, os candidatos excedentes são realocados para a ampla concorrência, respeitando os critérios mínimos de elegibilidade.

### 2. Classificação de Candidatos com Base em Critérios Técnicos e de Diversidade

#### a) Elegibilidade Técnica

Para ser considerado apto à capacitação, o candidato deve atender aos seguintes critérios:

- Estar cursando ensino superior a partir do 2º semestre;
- Ter previsão de formatura com pelo menos 13 meses de antecedência;
- Possuir computador e acesso à internet;
- Ter disponibilidade de horário compatível;
- Aceitar participar de estágio após a capacitação;
- Demonstrar interesse em atuar com CRM.

#### b) Distribuição de Vagas

Com base nos dados coletados, o sistema atribui o resultado final conforme as cotas e os critérios técnicos. As opções de retorno ao candidato são:

- **Aprovado**: Vaga confirmada, dentro da cota ou ampla concorrência;
- **Lista de Espera**: Vagas preenchidas, mas com possibilidade de realocação futura;
- **Não Aprovado**: Critérios técnicos não atendidos. A resposta é sempre respeitosa, sem detalhamento dos motivos da não aprovação.

### 3. Modelo de Classificação com Machine Learning

O núcleo inteligente do sistema é um **modelo de árvore de decisão**, treinado com **20.000 registros simulados** para representar diferentes perfis de candidatos. O modelo é responsável por analisar múltiplos fatores simultaneamente, atribuindo uma classificação final a cada candidatura.

#### Principais características do modelo:

- **Tipo**: Árvore de Decisão (DecisionTreeClassifier – Scikit-learn);
- **Dados de treinamento**: Sintéticos, balanceados e variados;
- **Variáveis analisadas**: Gênero, etnia, orientação sexual, deficiência, semestre atual, previsão de formatura, acesso a computador, nível de inglês, disponibilidade, interesse em CRM e estágio, entre outras;
- **Saída**: Aprovado ou não aprovado, com posterior aplicação da regra de distribuição por cotas.

Além da classificação, o sistema gera **métricas de desempenho**, como matriz de confusão, curva ROC e importância das variáveis (feature importance), permitindo avaliar e ajustar continuamente a assertividade do modelo.

### 4. Integração com o Google Sheets

Todas as candidaturas são registradas automaticamente em uma aba dedicada no Google Sheets por meio de autenticação via API do Google. A conexão é estabelecida com uma chave de serviço configurada através de variável de ambiente (`SERVICE_ACCOUNT_JSON`), garantindo segurança e sigilo dos dados.

A planilha armazena as seguintes colunas:

- Nome completo;
- E-mail;
- Telefone;
- Data de nascimento;
- Gênero;
- Etnia;
- Identificação LGBTQIA+;
- Identificação como PCD e tipo de deficiência;
- Curso, instituição, semestre atual e previsão de conclusão;
- Acesso a computador e internet;
- Nível de inglês;
- Participação anterior em capacitações;
- Interesse em CRM e estágio;
- Resultado da classificação;
- Data de inscrição.

### 5. Interface com Gradio

O formulário interativo foi desenvolvido com a biblioteca Gradio, proporcionando uma experiência acessível, intuitiva e responsiva aos candidatos.

#### Campos Dinâmicos

O sistema possui lógica condicional: campos adicionais são exibidos dependendo das respostas do candidato. Por exemplo, ao selecionar “Sim” para PCD, surgem campos específicos para descrição da deficiência e necessidades de acessibilidade.

### 6. Inteligência de Dados (Funcionalidade Complementar)

Para análise exploratória, o projeto oferece um módulo de clusterização com KMeans, que permite agrupar os candidatos de acordo com características como gênero, etnia e semestre. Essa funcionalidade, embora opcional, fornece insumos valiosos para ajustes de estratégia de inclusão e políticas futuras.

---

## Fluxo de Funcionamento

1. **Preenchimento do Formulário**: O candidato fornece seus dados de forma voluntária.
2. **Validação e Classificação com IA**: O modelo de árvore de decisão avalia a candidatura com base técnica e de diversidade.
3. **Resposta Automatizada**: O candidato recebe mensagem de aprovação, reprovação ou espera.
4. **Registro da Inscrição**: A candidatura é enviada automaticamente ao Google Sheets.
5. **Análise Preditiva (opcional)**: Clusters são gerados para compreensão de perfis.

---

## Melhorias Futuras

- Substituição do modelo atual por Random Forest ou XGBoost, para maior robustez e capacidade preditiva;
- Dashboard interativo: Visualização gráfica da distribuição dos inscritos, vagas por cota, taxa de aprovação e outros indicadores;
- Aprimoramento em acessibilidade: Inclusão de suporte multilíngue e leitores de tela para maior inclusão digital;
- Expansão do programa: Possibilidade de aplicação do mesmo modelo para outras áreas, como marketing digital, análise de dados e desenvolvimento front-end.

---

## Autoria

Este projeto foi idealizado, desenvolvido e documentado por **Crislene Nunes** durante o Bootcamp de LLM (Modelos de Linguagem de Grande Escala) da **SoulCode Academy**, com apoio institucional do **Grupo Petrópolis**. A iniciativa integra competências em desenvolvimento de sistemas, inteligência artificial aplicada e inclusão sociotécnica.

---

## Licença e Uso

Este repositório está disponível **exclusivamente para fins educacionais e demonstrativos**. É vedada a utilização comercial, modificação para uso corporativo ou qualquer redistribuição sem a autorização expressa da autora.


## Melhorias Futuras

- **Aprimoramento do Modelo de Classificação**: O uso de técnicas avançadas de aprendizado de máquina pode ser integrado para melhorar a precisão do modelo de seleção de candidatos.
  
- **Análise de Dados e Relatórios**: A geração de relatórios detalhados sobre as inscrições, distribuição de vagas e análise de diversidade pode ser automatizada para fornecer insights mais profundos.

- **Expansão para Outras Áreas**: O programa pode ser expandido para outras áreas além de CRM e IA, como marketing digital ou recursos humanos, aumentando as oportunidades de inclusão.



