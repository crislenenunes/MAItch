# Programa de Capacitação CRMAItch

Acesse o meu projeto de classificação de candidatos no Hugging Face [aqui](https://huggingface.co/spaces/Crislene/MAITch).


## Visão Geral

O **Programa de Capacitação CRMatch** é uma iniciativa focada em promover a inclusão de grupos diversos no mercado de trabalho, com ênfase em áreas de CRM e inteligência artificial. O programa oferece oportunidades de estágio e capacitação para pessoas de diferentes perfis, incluindo mulheres, negros, pardos, indígenas, pessoas com deficiência (PCD), pessoas neurodiversas, e membros da comunidade LGBTQIA+.

Este repositório contém o sistema de inscrição e avaliação dos candidatos, baseado em um formulário interativo criado com a biblioteca **Gradio** e integrado ao Google Sheets para registro das inscrições. O sistema é projetado para garantir a diversidade nas seleções, utilizando um modelo de classificação baseado em cotas e ampla concorrência.

## Funcionalidades

### 1. **Sistema de Cotas**

O sistema de cotas visa garantir uma distribuição justa das vagas, priorizando a inclusão de grupos que historicamente possuem menos acesso ao mercado de trabalho. A alocação das vagas é feita com base nos seguintes critérios:

- **PCD**: 10% das vagas são destinadas a pessoas com deficiência, com uma subcategoria para pessoas neurodiversas.
- **Raça**: 10% das vagas são destinadas a pessoas negras, pardas e indígenas.
- **Gênero**: 10% das vagas são destinadas a mulheres e pessoas não binárias.
- **LGBTQIA+**: 5% das vagas são destinadas a membros da comunidade LGBTQIA+.
- **Ampla Concorrência**: 65% das vagas são destinadas a candidatos sem especificação de cota, mas que ainda atendem aos critérios gerais do programa.

As vagas são alocadas com base em uma classificação que leva em consideração as respostas dos candidatos aos campos de **PCD**, **Raça**, **Gênero**, e **LGBTQIA+**. Quando as vagas reservadas pelas cotas são preenchidas, os candidatos vão para a categoria de **Ampla Concorrência**.

### 2. **Classificação de Candidatos**

A classificação dos candidatos é realizada com base nos seguintes critérios:

- **Critérios para Aprovação**: Para ser aprovado, o candidato precisa atender a um conjunto de critérios básicos de elegibilidade, como possuir computador e internet, disponibilidade de horário, e interesse no estágio. Além disso, os candidatos são avaliados para garantir que pelo menos 35% das vagas sejam preenchidas por grupos diversos.
  
- **Critérios de Reprovação**: Caso o candidato não preencha os critérios necessários, ele será reprovado e não poderá seguir na seleção. A mensagem de retorno será genérica e positiva, sem detalhamento dos motivos específicos de reprovação.

- **Lista de Espera**: Quando o número de vagas é preenchido, os candidatos restantes são colocados na lista de espera, com uma posição atribuída conforme a ordem de chegada. A lista de espera pode ser usada caso surjam vagas adicionais.

### 3. **Integração com o Google Sheets**

O sistema está integrado ao Google Sheets para registrar os dados dos candidatos de maneira eficiente. A conexão com o Google Sheets é configurada através de uma chave privada, usando o **Google API** para autenticação.

#### Configuração da Chave Privada

Para garantir a conexão segura com o Google Sheets, o projeto requer a chave de serviço (JSON) para acessar a planilha do Google. A chave é configurada através da variável de ambiente **SERVICE_ACCOUNT_JSON**, que contém as credenciais necessárias para a autenticação.

### 4. **Análise de Dados e Machine Learning (opcional)**

Embora não seja uma funcionalidade obrigatória, a análise de clusters dos dados é realizada usando o **KMeans** para agrupar candidatos com base em variáveis como gênero, etnia, e semestre. Esta funcionalidade ajuda a entender padrões no comportamento de candidatos e ajustar futuras seleções de maneira mais precisa.

### 5. **Formulário Gradio**

O formulário de inscrição é feito com a biblioteca **Gradio**, que permite uma interface visual simples e interativa. Os usuários preenchem informações pessoais, acadêmicas e profissionais, e o sistema classifica automaticamente suas candidaturas com base nos critérios mencionados.

#### Campos Condicionais

O formulário apresenta campos condicionais que aparecem dependendo das respostas do candidato. Por exemplo, se o candidato responder que é **Pessoa com Deficiência (PCD)**, campos adicionais para especificar o tipo de deficiência e necessidades de acessibilidade serão exibidos.

---

## Como Funciona

### 1. **Processamento de Candidaturas**

Quando um candidato se inscreve, as informações são verificadas com base nos critérios estabelecidos. Se a candidatura for aprovada, os dados são registrados no Google Sheets, e o candidato recebe uma resposta positiva. Caso contrário, ele é colocado na lista de espera ou informado que a vaga foi preenchida.

### 2. **Cadastro no Google Sheets**

A integração com o Google Sheets permite que todas as candidaturas sejam armazenadas de maneira organizada. A planilha de respostas está configurada para armazenar as seguintes colunas:

- **Nome**: Nome completo do candidato.
- **E-mail**: Endereço de e-mail para contato.
- **Telefone**: Número de telefone.
- **Data de Nascimento**: Data de nascimento do candidato.
- **Gênero**: Gênero do candidato.
- **Etnia**: Etnia do candidato.
- **LGBTQIA+**: Se o candidato é membro da comunidade LGBTQIA+.
- **PCD**: Se o candidato é uma pessoa com deficiência.
- **Capacitação Anterior**: Se o candidato já participou de algum programa de capacitação da CRMatch.
- **Interesse em CRM**: Se o candidato tem interesse em trabalhar com CRM.
- **Interesse em Estágio**: Se o candidato tem interesse em estágio.

### 3. **Modelagem e Algoritmos**

O modelo de árvore de decisão é usado para classificar os candidatos de acordo com as cotas e ampla concorrência. Ele verifica a elegibilidade dos candidatos para as vagas e atribui os resultados de "Apto", "Lista de Espera" ou "Não Apto".

---

## Melhorias Futuras

- **Aprimoramento do Modelo de Classificação**: O uso de técnicas avançadas de aprendizado de máquina pode ser integrado para melhorar a precisão do modelo de seleção de candidatos.
  
- **Análise de Dados e Relatórios**: A geração de relatórios detalhados sobre as inscrições, distribuição de vagas e análise de diversidade pode ser automatizada para fornecer insights mais profundos.

- **Expansão para Outras Áreas**: O programa pode ser expandido para outras áreas além de CRM e IA, como marketing digital ou recursos humanos, aumentando as oportunidades de inclusão.

---

Este README proporciona uma visão detalhada sobre o funcionamento do sistema, suas funcionalidades e a lógica por trás da distribuição das vagas. O sistema de cotas, classificação e integração com o Google Sheets são os pilares do projeto, que visa aumentar a diversidade e a inclusão no mercado de trabalho.

---

##Bootcamp
📌 Este projeto foi desenvolvido durante o Bootcamp de LLM (Modelos de Linguagem de Grande Escala) da SoulCode Academy, com apoio do Grupo Petrópolis.
