
# Sistema de Análise Automatizada de Testes A/B — Growth

Esta aplicação automatiza o processamento, a análise estatística e a geração de relatórios para testes A/B de cashback. O sistema realiza a limpeza de dados monetários, calcula métricas de negócio (`Net Revenue`, `ROI de Cashback` e `Ticket Médio`), executa testes de hipótese baseados na variabilidade diária e utiliza LLMs (Google GenAI SDK) para produzir relatórios executivos interpretativos.

---

## 📊 Armazenamento de Resultados & Tracking

Os resultados de todos os experimentos processados são registrados de forma estruturada:

* **Histórico Consolidado (CSV Local):** Gravado em `consolidado_testes.csv` na raiz do projeto. Contém as colunas solicitadas: *Nome do Teste*, *Descrição*, *Resultado* (incluindo o p-valor) e *Decisão Tomada*. Armazenado diretamente em [consolidado_testes.csv](https://github.com/lucaspaulo1/teste-meliuz/blob/main/consolidado_testes.csv) na raiz do projeto. Além disso, dentro da pasta `outputs/` as imagens e relatórios estão especificados
* **Integração com Google Sheets:** O sistema possui suporte nativo à API do Google Sheets (`gspread`). Caso a flag `"usar_google_sheets"` esteja definida como `true` no arquivo `config.json`, os dados serão inseridos diretamente na planilha em nuvem configurada.
* **Artefatos de Saída:** Os relatórios em Markdown (`.md`) e os gráficos de diagnóstico (`.png`) gerados pelo validador estatístico são exportados para o diretório `outputs/`.

---

## ⚙️ Decisões de Projeto e Arquitetura

### 1. Robustez Estatística (Welch's T-Test)
Análises baseadas apenas na soma acumulada de métricas podem ser distorcidas por outliers ou flutuações sazonais. Para mitigar o risco de "falsos vencedores", este sistema avalia as séries temporais diárias de `net_revenue` entre as duas principais variantes utilizando o **Teste T de Student para amostras independentes (Welch's T-Test)** via `scipy.stats`. Caso o p-valor calculado seja superior ao limite de significância definido (ex: $0.05$), o sistema determina um Empate Técnico e recomenda a variante de menor custo ou risco financeiro.

### 2. Tratamento de Erros e Degradação Suave (Graceful Degradation)
Para garantir a resiliência em ambiente de produção, as chamadas à API do Gemini e as operações de I/O são isoladas com tratamento de exceções (`try/except`). Caso a API externa apresente indisponibilidade (como erro 503), o pipeline captura a falha, registra o ocorrido via log e **prossegue com a gravação dos dados determinísticos na planilha**, impedindo a interrupção do tracking operacional.

### 3. Parametrizável via `config.json`
Regras de negócio e configurações de ambiente não foram codificadas de forma rígida (*hardcoded*). O comportamento do script é controlado pelo arquivo `config.json`, permitindo ajustar o nível de significância ($\alpha$), alternar o salvamento de gráficos e definir o destino do tracking (CSV ou Google Sheets).

### 4. Logging Estruturado
Substituiu-se o uso de comandos `print()` pelo módulo nativo `logging` do Python, padronizando as mensagens do sistema por níveis de severidade (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).

---

## 📂 Estrutura de Pastas

```text
├── data/                         # Datasets brutos de entrada (.csv)
├── src/                          # Módulos core da aplicação
│   ├── __init__.py
│   ├── data_processor.py         # ETL, parsing de moeda e agregação
│   ├── statistical_validator.py  # Teste T de Welch e geração de gráficos
│   ├── ai_analyst.py             # Integração com Google GenAI SDK
│   └── sheets_service.py         # Camada de persistência (CSV / Google Sheets)
├── outputs/                      # Relatórios MD e gráficos PNG exportados
├── config.json                   # Arquivo de configuração global
├── consolidado_testes.csv        # Histórico local de tracking
├── main.py                       # Ponto de entrada do script (CLI)
├── requirements.txt              # Dependências do projeto com versões fixadas
└── README.md                     # Documentação técnica

```

---

## 🛠️ Como Rodar o Projeto (Passo a Passo)

Os comandos abaixo são compatíveis com Windows, macOS e Linux.

### 1. Clonar o Repositório e Acessar o Diretório

```bash
git clone <link-do-seu-repositorio>
cd teste-meliuz

```

### 2. Criar e Ativar o Ambiente Virtual (Venv)

* **Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows (Prompt de Comando - CMD):**
```cmd
python -m venv venv
call venv\Scripts\activate.bat

```


* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```



### 3. Instalar as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

### 4. Configurar a Chave da API do Gemini

Defina a variável de ambiente necessária para autenticação no modelo de linguagem.

* **Linux / macOS:**
```bash
export GEMINI_API_KEY="sua_chave_aqui"

```


* **Windows (CMD):**
```cmd
set GEMINI_API_KEY=sua_chave_aqui

```


* **Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="sua_chave_aqui"

```



### 5. Executar a Análise

Passe o caminho do arquivo `.csv` desejado como argumento para o script principal:

```bash
python main.py data/dataset_01_parceiroA.csv

```

---

## ⚙️ Customização do Arquivo `config.json`

O arquivo `config.json` na raiz gerencia o comportamento do pipeline:

```json
{
  "alpha_significancia": 0.05,
  "salvar_graficos": true,
  "usar_google_sheets": false,
  "nome_planilha_google": "Tracking de Testes A/B - Growth",
  "diretorio_outputs": "outputs"
}

```

*Nota: Para utilizar a integração com o Google Sheets (`"usar_google_sheets": true`), é necessário gerar um arquivo de credenciais de Conta de Serviço no Google Cloud Console, salvá-lo na raiz como `credentials.json` e compartilhar a planilha alvo com o e-mail cadastrado na chave.*
