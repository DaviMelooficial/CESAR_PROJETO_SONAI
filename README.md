# 🚀 Sistema de Análise e Visualização de Documentos

**Uma solução completa para extração, análise e visualização de dados de múltiplos tipos de documentos**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Produção-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## 📋 Visão Geral

Este sistema oferece uma **solução integrada** para processamento automatizado de documentos corporativos, incluindo extração de dados, análise exploratória e criação de visualizações interativas. Desenvolvido para organizações que precisam analisar grandes volumes de documentos em diferentes formatos.

### 🎯 **Características Principais**

- ✅ **Extração Multi-formato**: PDF, DOC/DOCX, CSV, XLSX
- ✅ **Análise Automatizada**: Estatísticas, qualidade de dados, insights
- ✅ **Visualizações Interativas**: Gráficos Plotly com análise textual
- ✅ **Pipeline Completo**: Da extração à visualização final
- ✅ **Relatórios Automáticos**: JSON estruturado e análises detalhadas
- ✅ **Robustez**: Tratamento de erros e fallbacks automáticos

---

## 🏗️ Arquitetura da Solução

```
📁 analise_visualizacao/
├── 📁 data/
│   ├── 📁 raw/                    # Documentos originais
│   └── 📁 processed/              # Dados extraídos e limpos
├── 📁 scripts/
│   ├── 📄 extrator_principal.py   # CLI unificado
│   ├── 📄 extrator_pdf.py         # Extrator para PDFs
│   ├── 📄 extrator_doc.py         # Extrator para DOC/DOCX
│   └── 📄 extrator_csv_xlsx.py    # Extrator para CSV/XLSX
├── 📁 notebooks/
│   ├── 📓 Analise_Exploratoria_Dados.ipynb
│   └── 📓 Visualizacoes_Avancadas.ipynb
├── 📁 reports/                    # Relatórios gerados
├── 📁 docs/                       # Documentação
└── 📄 README.md                   # Este arquivo
```

---

## ⚡ Início Rápido

### **1. Pré-requisitos**

```bash
# Python 3.8 ou superior
python --version

# Git (opcional)
git --version
```

### **2. Instalação das Dependências**

**Opção A - Instalação Automática:**
```bash
# No Windows
.\instalar_dependencias.bat

# No Linux/Mac
pip install -r requirements.txt
```

**Opção B - Instalação Manual:**
```bash
pip install pandas numpy matplotlib seaborn plotly
pip install openpyxl PyPDF2 pdfplumber python-docx
pip install wordcloud textstat jupyter notebook
```

### **3. Estrutura de Pastas**

O sistema **cria automaticamente** todas as pastas necessárias. Apenas coloque seus documentos na pasta `data/raw/`.

### **4. Executar o Sistema**

```bash
# Navegar para a pasta do projeto
cd analise_visualizacao

# Executar o extrator principal
python scripts/extrator_principal.py

# Ou usar argumentos específicos
python scripts/extrator_principal.py --tipo pdf --arquivo documento.pdf
```

---

## 📊 Funcionalidades Detalhadas

### **🔧 Sistema de Extração**

| Formato | Status | Capacidades |
|---------|--------|-------------|
| **PDF** | ✅ | Texto, metadados, tabelas, estatísticas textuais |
| **DOC/DOCX** | ✅ | Texto completo, estatísticas, metadados |
| **CSV** | ✅ | Dados estruturados, análise de colunas, limpeza |
| **XLSX** | ✅ | Múltiplas planilhas, estatísticas, validação |

### **📈 Análise Exploratória**

- **Estatísticas Textuais**: Palavras, densidade lexical, complexidade
- **Qualidade de Dados**: Valores nulos, inconsistências, limpeza automática
- **Análise Temporal**: Padrões ao longo do tempo
- **Correlações**: Relações entre variáveis

### **🎨 Visualizações Avançadas**

1. **📊 Análise de Distribuição**
   - Gráfico de barras + pizza
   - Comparação de tipos de documento
   - Análise de proporções

2. **📈 Complexidade de Documentos**
   - Gráfico de bolhas interativo
   - Multivariedade (palavras × densidade × tabelas)
   - Análise por quadrantes

3. **🎯 Dashboard Temporal e Qualidade**
   - 4 visualizações integradas
   - Evolução temporal
   - Indicadores de qualidade

4. **☁️ Nuvem de Palavras**
   - Análise de padrões temáticos
   - Identificação de focos organizacionais

---

## 🎯 Casos de Uso

### **Para Analistas de Dados**
```bash
# Análise rápida de um conjunto de documentos
python scripts/extrator_principal.py --tipo todos

# Focar apenas em dados estruturados
python scripts/extrator_principal.py --tipo csv,xlsx
```

### **Para Gestores**
1. Execute o extrator principal
2. Abra `notebooks/Analise_Exploratoria_Dados.ipynb`
3. Visualize insights no `reports/resumo_analise_exploratoria.json`

### **Para Pesquisadores**
1. Coloque documentos em `data/raw/`
2. Execute análise completa
3. Use `notebooks/Visualizacoes_Avancadas.ipynb` para insights visuais

---

## 🔧 Configuração Avançada

### **Personalizar Extração**

```python
# Exemplo de uso programático
from scripts.extrator_principal import ExtractorPrincipal

extrator = ExtractorPrincipal()
resultados = extrator.processar_todos_arquivos()
```

### **Configurar Análise**

```python
# Personalizar parâmetros no notebook
PASTA_DADOS = Path("../data/processed")
FILTROS_QUALIDADE = {'taxa_nulos_max': 0.1}
```

---

## 📋 Exemplos de Saída

### **Relatório JSON**
```json
{
  "data_analise": "2025-09-28 15:30:00",
  "total_documentos": 15,
  "tipos_documento": {
    "PDF": 8,
    "XLSX": 4,
    "DOC": 2,
    "CSV": 1
  },
  "qualidade_dados": {
    "taxa_media_nulos": 0.03,
    "status": "Excelente"
  }
}
```

### **Insights Textuais**
```
📊 RESUMO EXECUTIVO:
  📁 Total de documentos: 15
  📝 Documentos de texto: 10
  📊 Documentos tabulares: 5

🎯 PRINCIPAIS DESCOBERTAS:
  1️⃣ PDF é o formato predominante (53.3%)
  2️⃣ Documentos extensos (média: 2,847 palavras)
  3️⃣ Excelente qualidade (97% sem valores nulos)
```

---

## 🛠️ Troubleshooting

### **Problemas Comuns**

#### **"Módulo não encontrado"**
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

#### **"Arquivo não encontrado"**
- Verificar se os arquivos estão em `data/raw/`
- Confirmar extensões suportadas (.pdf, .docx, .csv, .xlsx)

#### **"Erro de encoding"**
- O sistema detecta automaticamente o encoding
- Para forçar UTF-8: editar configurações no script

#### **"Jupyter não abre"**
```bash
# Instalar/atualizar Jupyter
pip install --upgrade jupyter notebook
jupyter notebook --generate-config
```

### **Performance**

- **Documentos grandes**: O sistema processa automaticamente em chunks
- **Muitos arquivos**: Use `--tipo` para processar seletivamente
- **Memória baixa**: Processe por tipo de documento separadamente

---

## 📈 Roadmap e Melhorias

### **v2.0 (Planejado)**
- [ ] Interface web com Streamlit
- [ ] API REST para integração
- [ ] Suporte a mais formatos (TXT, RTF, PPT)
- [ ] Machine Learning para classificação automática
- [ ] Dashboard em tempo real

### **v2.1 (Futuro)**
- [ ] Integração com bancos de dados
- [ ] Processamento distribuído
- [ ] OCR para documentos escaneados
- [ ] Análise de sentimentos

---

## 🤝 Como Contribuir

1. **Fork** o projeto
2. **Clone** localmente
3. **Instale** dependências de desenvolvimento
4. **Teste** suas mudanças
5. **Submeta** um Pull Request

### **Áreas que Precisam de Ajuda**
- 🐛 Testes automatizados
- 📚 Documentação adicional
- 🎨 Novos tipos de visualização
- ⚡ Otimizações de performance

---

## 📞 Suporte e Contato

### **Para Usuários**
- 📖 **Documentação**: Consulte este README e os notebooks
- 🐛 **Bugs**: Abra uma issue no repositório
- 💡 **Sugestões**: Use as discussions do GitHub

### **Para Desenvolvedores**
- 🛠️ **API**: Documentação inline nos scripts
- 🔧 **Extensões**: Veja `docs/desenvolvimento.md`
- 🤝 **Colaboração**: Siga o guia de contribuição

---

## 📜 Licença e Créditos

**MIT License** - Livre para uso comercial e pessoal.

### **Tecnologias Utilizadas**
- **Python**: Linguagem principal
- **Pandas/NumPy**: Processamento de dados
- **Plotly**: Visualizações interativas
- **Jupyter**: Ambiente de análise
- **PyPDF2/pdfplumber**: Extração de PDFs
- **python-docx**: Processamento de documentos Word

### **Créditos**
Desenvolvido com foco em **robustez**, **usabilidade** e **extensibilidade** para atender necessidades reais de análise documental corporativa.

---

## 🎯 Status do Projeto

| Componente | Status | Última Atualização |
|------------|--------|-------------------|
| **Extratores** | ✅ Completo | 28/09/2025 |
| **Análise Exploratória** | ✅ Completo | 28/09/2025 |
| **Visualizações** | ✅ Completo | 28/09/2025 |
| **Documentação** | ✅ Completo | 28/09/2025 |
| **Testes** | 🔄 Em andamento | - |
| **Interface Web** | 📅 Planejado | - |

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**

**🚀 Comece agora mesmo colocando seus documentos em `data/raw/` e executando o sistema!**