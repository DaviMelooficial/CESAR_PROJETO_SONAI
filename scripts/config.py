# Configuração do Projeto - Sistema de Análise e Visualização

"""
Arquivo de configuração centralizada para o projeto.
Contém constantes, caminhos e configurações utilizadas pelos scripts.
"""

from pathlib import Path
import os

# =====================================
# INFORMAÇÕES DO PROJETO
# =====================================
PROJECT_NAME = "Sistema de Análise e Visualização de Relatórios"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "Sistema de Análise e Visualização"
PROJECT_DATE = "Setembro 2025"

# =====================================
# CAMINHOS DO PROJETO
# =====================================
# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Diretórios de dados
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Diretórios de código
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Diretórios de saída
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"

# =====================================
# CONFIGURAÇÕES DE EXTRAÇÃO
# =====================================
# Formatos de arquivo suportados
SUPPORTED_FORMATS = {
    'pdf': ['.pdf'],
    'doc': ['.doc', '.docx'],
    'csv': ['.csv'],
    'xlsx': ['.xlsx', '.xls']
}

# Formatos de saída
OUTPUT_FORMATS = ['txt', 'json', 'csv']
DEFAULT_OUTPUT_FORMAT = 'json'

# Configurações de encoding
DEFAULT_ENCODING = 'utf-8'
FALLBACK_ENCODINGS = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-16']

# =====================================
# CONFIGURAÇÕES DE ANÁLISE
# =====================================
# Pandas
PANDAS_MAX_COLUMNS = None
PANDAS_MAX_ROWS = 1000
PANDAS_WIDTH = None
PANDAS_MAX_COLWIDTH = 100

# Estatísticas
MIN_WORDS_FOR_TEXT_ANALYSIS = 10
MAX_DISPLAY_ROWS = 10

# =====================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# =====================================
# Matplotlib
MATPLOTLIB_STYLE = 'seaborn-v0_8-darkgrid'
MATPLOTLIB_FIGURE_SIZE = (12, 8)
MATPLOTLIB_FONT_SIZE = 10
MATPLOTLIB_DPI = 100

# Plotly
PLOTLY_TEMPLATE = "plotly_white"
PLOTLY_DEFAULT_HEIGHT = 600
PLOTLY_DEFAULT_WIDTH = 1000

# Cores personalizadas
CUSTOM_COLORS = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4', 
    'tertiary': '#45B7D1',
    'quaternary': '#96CEB4',
    'accent': '#FFEAA7',
    'warning': '#FFD93D',
    'error': '#E74C3C',
    'success': '#2ECC71',
    'info': '#3498DB',
    'dark': '#2E4057'
}

# Paleta de cores para gráficos
COLOR_PALETTE = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                '#95A5A6', '#E74C3C', '#2ECC71', '#3498DB', '#9B59B6']

# =====================================
# CONFIGURAÇÕES DE PROCESSAMENTO DE TEXTO
# =====================================
# Stopwords customizadas
CUSTOM_STOPWORDS = {
    'portuguese': ['de', 'da', 'do', 'das', 'dos', 'e', 'o', 'a', 'os', 'as', 
                  'em', 'para', 'com', 'por', 'um', 'uma', 'uns', 'umas', 'na', 'no'],
    'english': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
               'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'],
    'common': ['v', 'version', 'doc', 'pdf', 'csv', 'xlsx', 'final', 'temp']
}

# Configurações para nuvem de palavras
WORDCLOUD_CONFIG = {
    'width': 1200,
    'height': 600,
    'background_color': 'white',
    'max_words': 50,
    'colormap': 'Set2',
    'relative_scaling': 0.5,
    'random_state': 42
}

# =====================================
# CONFIGURAÇÕES DE LOGGING
# =====================================
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

# =====================================
# CONFIGURAÇÕES DE PERFORMANCE
# =====================================
# Tamanhos máximos de arquivo (em MB)
MAX_FILE_SIZE = {
    'pdf': 50,
    'doc': 30,
    'csv': 100,
    'xlsx': 50
}

# Configurações de memória
CHUNK_SIZE = 1000  # Para processamento em lotes
MAX_MEMORY_USAGE = '2GB'  # Limite de memória

# =====================================
# METADADOS DE SAÍDA
# =====================================
# Informações incluídas nos arquivos de saída
OUTPUT_METADATA = {
    'project': PROJECT_NAME,
    'version': PROJECT_VERSION,
    'author': PROJECT_AUTHOR,
    'generated_by': 'Sistema de Extração Automatizado',
    'encoding': DEFAULT_ENCODING
}

# =====================================
# CONFIGURAÇÕES DE QUALIDADE
# =====================================
# Thresholds para qualidade dos dados
QUALITY_THRESHOLDS = {
    'excellent': {'null_rate': 0.01, 'completeness': 0.99},
    'good': {'null_rate': 0.05, 'completeness': 0.95},
    'acceptable': {'null_rate': 0.15, 'completeness': 0.85},
    'poor': {'null_rate': 0.30, 'completeness': 0.70}
}

# Métricas de complexidade textual
TEXT_COMPLEXITY = {
    'low': {'words': (0, 500), 'density': (0, 0.1)},
    'medium': {'words': (500, 2000), 'density': (0.1, 0.2)},
    'high': {'words': (2000, 5000), 'density': (0.2, 0.3)},
    'very_high': {'words': (5000, float('inf')), 'density': (0.3, 1.0)}
}

# =====================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# =====================================
# Debug
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
VERBOSE_LOGGING = os.getenv('VERBOSE', 'False').lower() == 'true'

# Teste
SAMPLE_DATA_SIZE = 100  # Número de registros para dados de exemplo
RANDOM_SEED = 42  # Para reprodutibilidade

# =====================================
# FUNÇÕES AUXILIARES DE CONFIGURAÇÃO
# =====================================
def get_color_by_type(file_type: str) -> str:
    """
    Retorna cor padrão para um tipo de arquivo.
    """
    color_map = {
        'PDF': CUSTOM_COLORS['primary'],
        'DOC': CUSTOM_COLORS['secondary'],
        'CSV': CUSTOM_COLORS['tertiary'],
        'XLSX': CUSTOM_COLORS['quaternary']
    }
    return color_map.get(file_type.upper(), CUSTOM_COLORS['accent'])

def get_file_type_from_extension(file_path: str) -> str:
    """
    Determina o tipo de arquivo baseado na extensão.
    """
    extension = Path(file_path).suffix.lower()
    
    for file_type, extensions in SUPPORTED_FORMATS.items():
        if extension in extensions:
            return file_type.upper()
    
    return 'UNKNOWN'

def create_directories():
    """
    Cria todos os diretórios necessários para o projeto.
    """
    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        REPORTS_DIR,
        DOCS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
    return True

def get_quality_level(null_rate: float) -> str:
    """
    Determina o nível de qualidade baseado na taxa de valores nulos.
    """
    if null_rate <= QUALITY_THRESHOLDS['excellent']['null_rate']:
        return 'Excelente'
    elif null_rate <= QUALITY_THRESHOLDS['good']['null_rate']:
        return 'Boa'
    elif null_rate <= QUALITY_THRESHOLDS['acceptable']['null_rate']:
        return 'Aceitável'
    else:
        return 'Ruim'

# =====================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# =====================================
def validate_config():
    """
    Valida se as configurações estão corretas.
    """
    errors = []
    
    # Verificar se os diretórios podem ser criados
    try:
        create_directories()
    except Exception as e:
        errors.append(f"Erro ao criar diretórios: {e}")
    
    # Verificar formato de saída padrão
    if DEFAULT_OUTPUT_FORMAT not in OUTPUT_FORMATS:
        errors.append(f"Formato padrão {DEFAULT_OUTPUT_FORMAT} não está em {OUTPUT_FORMATS}")
    
    # Verificar cores
    if len(COLOR_PALETTE) < 5:
        errors.append("Paleta de cores deve ter pelo menos 5 cores")
    
    return errors

# Executar validação ao importar
if __name__ == "__main__":
    validation_errors = validate_config()
    if validation_errors:
        print("❌ Erros de configuração encontrados:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("✅ Configuração validada com sucesso!")
        print(f"📁 Diretórios criados em: {PROJECT_ROOT}")