# Avaliação Empírica de Desempenho, Consumo Energético e Custos em LLMs Locais

Este repositório contém os scripts de automação, arquivos de configuração e dados brutos do estudo empírico sobre o consumo de energia, emissões de carbono, custos financeiros e desempenho operacional de Modelos de Linguagem de Grande Porte (LLMs) executados localmente em ambiente Linux.

O objetivo do projeto é avaliar conjuntamente a eficiência computacional e o impacto ambiental de modelos abertos durante a inferência de requisições padronizadas.

---

## 📌 Visão Geral do Projeto

A execução local de LLMs oferece privacidade e autonomia, porém impõe custos computacionais e energéticos significativos. Este estudo analisa comparativamente cinco arquiteturas de referência submetidas a um conjunto de **10.000 prompts**, mensurando:

- **Desempenho Operacional:** Tempo de resposta, latência média por pergunta e taxa de geração de tokens (tokens/segundo).
- **Recursos de Hardware:** Uso do pico de CPU (%), memória RAM (GB) e operações de leitura/escrita em disco (MB).
- **Impacto Ambiental:** Consumo energético total (Wh) da CPU/GPU e estimativa de emissões de $\text{CO}_2$ (g$\text{CO}_2$ e g$\text{CO}_2$/1k tokens) via CodeCarbon.
- **Custo Financeiro:** Conversão do consumo elétrico em custo monetário local (R$/kWh e R$/1k tokens).

---

## 🤖 Modelos Avaliados

Todos os modelos foram executados via plataforma **Ollama** sob configurações padronizadas:

| Modelo | Parâmetros | Descrição / Foco |
| :--- | :---: | :--- |
| **Llama-3** | 8B | Modelo aberto de uso geral de alto desempenho |
| **Qwen2** | 7B | Modelo multilíngue otimizado |
| **Gemma3** | 4B | Arquitetura leve com alto volume de geração por resposta |
| **Phi-3.5** | 3.8B | Modelo compacto focado em eficiência |
| **DeepSeek-R1** | 8B | Modelo focado em raciocínio e tarefas estruturadas |

---

## 🔬 Metodologia Experimental

O processo experimental foi organizado em 7 etapas principais:

1. **Definição do Ambiente:** Configuração do sistema operacional Linux, isolamento de processos secundários e preparação do ambiente de monitoramento.
2. **Seleção dos Modelos:** Escolha de 5 LLMs com diferentes volumes de parâmetros e características de treinamento.
3. **Elaboração e Aplicação da Base:** Submissão idêntica de uma base contendo **10.000 perguntas** abrangendo variados tópicos, extensões e níveis de complexidade.
4. **Execução e Coleta de Dados:** Automação do envio via API/Ollama com registro de logs de CPU, RAM, I/O e métricas de inferência.
5. **Mensuração Ambiental:** Monitoramento do consumo energético em Wh (CPU e GPU) e cálculo do $g\text{CO}_2$ associado utilizando o CodeCarbon.
6. **Cálculo Financeiro:** Conversão da energia consumida (kWh) para valor monetário com base na tarifa regional estipulada (R$ 0,88 / kWh).
7. **Análise Comparativa:** Consolidação das métricas para avaliação do *trade-off* entre desempenho, custo e pegada de carbono.

---

## 💻 Configuração do Ambiente de Hardware e Software

- **Sistema Operacional:** Linux
- **Gerenciador de LLMs:** Ollama
- **Ferramenta de Rastreamento de Carbono:** CodeCarbon
- **Linguagem Principal:** Python 3.x

---

## 📂 Estrutura do Repositório
```
├── data/
│   ├── prompts.json           # Base de dados com as 10.000 perguntas
│   └── raw_results/           # Logs e saídas brutas obtidas nos testes
├── scripts/
│   ├── run_experiments.py     # Automação do envio de requisições via Ollama
│   ├── monitor_resources.py   # Coleta de métricas de CPU, RAM e Disco
│   └── energy_tracker.py      # Integração com o CodeCarbon para consumo elétrico
├── analysis/
│   └── generate_tables.py     # Processamento dos dados e geração das tabelas
├── requirements.txt           # Dependências do projeto Python
└── README.md                  # Documentação do projeto
```
---
## 🚀 Como Reproduzir os Experimentos

Siga os passos abaixo para preparar o ambiente, baixar os modelos e executar a coleta de dados completa.

---

### Passo 1: Instalação do Ollama
Instale a plataforma Ollama no seu ambiente Linux para gerenciar o carregamento e a inferência dos modelos:

```
curl -fsSL https://ollama.com/install.sh | sh
```
---

### Passo 2: Download dos Modelos
Faça o download de todos os cinco modelos avaliados no estudo diretamente pelo terminal:

```
ollama pull llama3:8b
ollama pull qwen2:7b
ollama pull gemma3:4b
ollama pull phi3.5
ollama pull deepseek-r1:8b
```
---
### Passo 3: Clonar o Repositório e Criar o Ambiente Virtual (venv)

1. Clone o repositório para a sua máquina local e acesse a pasta do projeto:
```
git clone https://github.com/avaliacaoLLMs/LLMs.git
cd LLMs
```
---
2. Crie o ambiente virtual (venv) : 
```
python3 -m venv venv
```
---
3. Ative o ambiente virtual :
```
source venv/bin/activate
```
---
4. Instale as dependências no ambiente virtual ativo :
```
pip install -r requirements.txt
```
5. Execução do Experimento
```
python experimento.py
```











                   
