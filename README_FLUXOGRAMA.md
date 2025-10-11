# Sistema de Análise e Visualização de Relatórios - Fluxograma Completo

## Visão Geral do Projeto

Este documento descreve o fluxo completo do sistema de análise e visualização de relatórios da MC Sonae, desde a extração de dados de múltiplos formatos até a apresentação final em dashboard interativo.

## Arquitetura do Sistema

```mermaid
graph TD
    A[Documentos de Origem] --> B[Sistema de Extração]
    B --> C[Dados Processados]
    C --> D[Jupyter Notebook - EDA]
    D --> E[Insights e Análises]
    E --> F[Dashboard Streamlit]
    F --> G[Usuário Final]
    
    A1[PDF] --> B
    A2[DOC/DOCX] --> B
    A3[CSV] --> B
    A4[XLSX] --> B
    
    B1[extrator_pdf.py] --> C
    B2[extrator_doc.py] --> C
    B3[extrator_csv_xlsx.py] --> C
    B4[extrator_principal.py] --> C
    
    C1[JSON] --> D
    C2[CSV] --> D
    C3[TXT] --> D
```

## Fluxograma Detalhado

### 1. Camada de Dados de Origem 📁

**Localização**: `data/raw/`

#### Tipos de Arquivos Suportados:
- **PDF**: Relatórios executivos, documentos corporativos
- **DOC/DOCX**: Atas de reunião, relatórios departamentais
- **CSV**: Dados tabulares, métricas de projetos
- **XLSX**: Planilhas complexas, dashboards financeiros

#### Exemplo de Estrutura:
```
data/raw/
├── Relatorio_projetos.csv
├── RELATÓRIO DE PROJETOS 2024.pdf
├── Exemplo_doc.docx
└── outros_documentos/
```

### 2. Sistema de Extração 🔧

#### 2.1 Extratores Especializados

##### **extrator_pdf.py**
```python
# Funcionalidades:
- PyPDF2: Extração básica de texto
- pdfplumber: Extração avançada + tabelas
- Metadados: Autor, data criação, número páginas
- Fallback automático entre bibliotecas
```

**Saídas**:
- Texto completo estruturado
- Tabelas extraídas (se existirem)
- Metadados do documento

##### **extrator_doc.py**
```python
# Funcionalidades:
- python-docx: Processamento DOCX
- zipfile: Método alternativo XML
- Extração de parágrafos numerados
- Preservação de estilos
```

**Saídas**:
- Parágrafos estruturados
- Tabelas incorporadas
- Metadados de autoria

##### **extrator_csv_xlsx.py**
```python
# Funcionalidades:
- pandas: Análise robusta de dados
- Detecção automática de encoding
- Estatísticas descritivas
- Validação de qualidade
```

**Saídas**:
- Dados estruturados em JSON
- Metadados estatísticos
- Análise de qualidade

#### 2.2 Orquestrador Principal

##### **extrator_principal.py**
```python
# Funcionalidades:
- Interface unificada CLI/interativa
- Processamento em lote
- Relatórios de execução
- Tratamento de erros robusto
```

**Comando de Execução**:
```bash
python extrator_principal.py --todos --formato json
```

### 3. Camada de Dados Processados 📊

**Localização**: `data/processed/`

#### Estrutura de Saída:
```
data/processed/
├── Relatorio_projetos_dados.json
├── RELATÓRIO DE PROJETOS 2024_dados.json
├── Exemplo_doc_dados.json
└── metadados/
    ├── logs_execucao.txt
    └── relatorio_processamento.txt
```

#### Formato JSON Padrão:
```json
{
  "dados": [...],
  "metadados": {
    "encoding": "utf-8",
    "num_linhas": 4,
    "tamanho_arquivo": 681,
    "data_processamento": "2024-10-11"
  },
  "estatisticas": {...},
  "qualidade": {
    "completude": 100,
    "consistencia": "alta"
  }
}
```

### 4. Análise Exploratória (Jupyter Notebook) 📈

**Arquivo**: `notebooks/analise.ipynb`

#### Etapas da Análise:

##### 4.1 Preparação dos Dados
```python
# Carregamento e limpeza
df = pd.read_csv('../data/processed/dados_consolidados.csv')
df['Data_Inicio'] = pd.to_datetime(df['Data_Inicio'])
df['Duracao_meses'] = (df['Data_Fim'] - df['Data_Inicio']).dt.days / 30.44
```

##### 4.2 Análise Univariada
- Distribuição de investimentos
- Status dos projetos
- Categorização por departamento
- Métricas de duração

##### 4.3 Análise Bivariada
- Correlação investimento vs progresso
- Relação duração vs performance
- Análise temporal (Gantt)
- Eficiência departamental

##### 4.4 Insights e Storytelling
- Dashboard executivo
- Ranking de performance
- Recomendações estratégicas
- Limitações e estudos futuros

#### Outputs da Análise:
```python
# Métricas Calculadas:
- ROI_Progresso = Progresso(%) / (Investimento/1000)
- Eficiencia_Departamental = Progresso_Medio / Investimento_Total
- Correlacao_Investimento_Progresso = 0.803
- Taxa_Conclusao = 25%
```

### 5. Dashboard Streamlit 🚀

#### 5.1 Estrutura Proposta

**Arquivo**: `dashboard/app.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Configuração da página
st.set_page_config(
    page_title="MC Sonae - Dashboard de Projetos",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

#### 5.2 Componentes do Dashboard

##### **Sidebar - Filtros**
```python
# Filtros interativos
departamento_filter = st.sidebar.multiselect("Departamentos")
status_filter = st.sidebar.selectbox("Status")
periodo_filter = st.sidebar.date_input("Período")
```

##### **Métricas Principais**
```python
# KPIs no topo
col1, col2, col3, col4 = st.columns(4)
col1.metric("Investimento Total", "€415,000")
col2.metric("Progresso Médio", "63.8%")
col3.metric("Taxa Conclusão", "25%")
col4.metric("Projetos Ativos", "3")
```

##### **Visualizações Interativas**
- Gráfico de progresso por projeto
- Timeline de execução (Gantt)
- Análise de investimento vs ROI
- Distribuição departamental
- Mapa de calor de correlações

##### **Tabelas Dinâmicas**
- Ranking de projetos por eficiência
- Status detalhado por departamento
- Cronograma de entregas
- Análise de riscos

#### 5.3 Funcionalidades Avançadas

##### **Exportação de Relatórios**
```python
# Download de dados processados
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(filtered_data)
st.download_button("Download CSV", csv, "relatorio.csv")
```

##### **Alertas Inteligentes**
```python
# Sistema de alertas baseado em métricas
if projeto_progress < 50 and dias_deadline < 30:
    st.error(f"⚠️ Projeto {nome} em risco!")
```

### 6. Fluxo de Execução Completo 🔄

#### 6.1 Pipeline de Dados

```bash
# 1. Extração de dados
cd scripts/
python extrator_principal.py --todos --formato json

# 2. Análise exploratória
cd ../notebooks/
jupyter notebook analise.ipynb

# 3. Dashboard
cd ../dashboard/
streamlit run app.py
```

#### 6.2 Automação com Scripts

**Arquivo**: `run_pipeline.py`
```python
import subprocess
import logging
from datetime import datetime

def run_extraction():
    """Executa extração de dados"""
    result = subprocess.run([
        'python', 'scripts/extrator_principal.py', 
        '--todos', '--formato', 'json'
    ])
    return result.returncode == 0

def update_dashboard_data():
    """Atualiza dados para dashboard"""
    # Consolidar JSONs em formato dashboard
    consolidated_data = merge_extracted_data()
    save_dashboard_data(consolidated_data)

def main():
    if run_extraction():
        update_dashboard_data()
        print("Pipeline executado com sucesso!")
    else:
        print("Erro na extração de dados")
```

### 7. Estrutura de Arquivos Final 📂

```
project_eda2/
├── data/
│   ├── raw/                    # Dados originais
│   ├── processed/              # Dados extraídos
│   └── dashboard/              # Dados para dashboard
├── scripts/                    # Sistema de extração
├── notebooks/                  # Análise exploratória
├── dashboard/                  # Aplicação Streamlit
│   ├── app.py
│   ├── components/
│   │   ├── charts.py
│   │   ├── metrics.py
│   │   └── filters.py
│   └── utils/
│       ├── data_loader.py
│       └── calculations.py
├── config/                     # Configurações
├── logs/                       # Logs de execução
└── docs/                       # Documentação
```

### 8. Considerações Técnicas 🛠️

#### 8.1 Performance
- Cache de dados com `@st.cache_data`
- Lazy loading para datasets grandes
- Otimização de queries para filtros

#### 8.2 Segurança
- Validação de inputs
- Sanitização de dados
- Controle de acesso por usuário

#### 8.3 Escalabilidade
- Modularização do código
- Configuração via variáveis de ambiente
- Suporte a múltiplas fontes de dados

### 9. Roadmap de Implementação 📅

#### Fase 1: MVP (2 semanas)
- [ ] Dashboard básico com métricas principais
- [ ] Integração com dados extraídos
- [ ] Visualizações core (barras, pizza, linha)

#### Fase 2: Funcionalidades Avançadas (3 semanas)
- [ ] Filtros dinâmicos
- [ ] Exportação de relatórios
- [ ] Sistema de alertas

#### Fase 3: Otimização (2 semanas)
- [ ] Performance tuning
- [ ] Testes automatizados
- [ ] Documentação completa

### 10. Métricas de Sucesso 📊

#### KPIs do Sistema:
- **Tempo de processamento**: < 30 segundos
- **Uptime do dashboard**: > 99%
- **Precisão da extração**: > 95%
- **Satisfação do usuário**: > 8/10

#### Métricas de Negócio:
- **Redução tempo análise**: 70%
- **Aumento insights**: 3x mais descobertas
- **ROI do projeto**: Positivo em 6 meses

---

## Comandos de Execução Rápida

```bash
# Pipeline completo
python run_pipeline.py

# Apenas extração
python scripts/extrator_principal.py --todos

# Apenas dashboard
streamlit run dashboard/app.py --server.port 8501

# Desenvolvimento
jupyter notebook notebooks/analise.ipynb
```

---

*Este documento serve como guia técnico para implementação e manutenção do sistema de análise de relatórios corporativos.*