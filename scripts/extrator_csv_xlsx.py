"""
Script para extração e processamento de dados de arquivos CSV/XLSX
Autor: Sistema de Análise e Visualização
Data: Setembro 2025
"""

import os
import json
import csv
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtratorCSVXLSX:
    """
    Classe para extrair e processar dados de arquivos CSV/XLSX
    """
    
    def __init__(self, pasta_origem: str = "../data/raw", pasta_destino: str = "../data/processed"):
        self.pasta_origem = Path(pasta_origem)
        self.pasta_destino = Path(pasta_destino)
        
        # Criar pasta de destino se não existir
        self.pasta_destino.mkdir(parents=True, exist_ok=True)
        
    def detectar_encoding(self, caminho_csv: str) -> str:
        """
        Detecta o encoding de um arquivo CSV
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(caminho_csv, 'r', encoding=encoding) as f:
                    f.read(1024)  # Tentar ler os primeiros 1024 caracteres
                return encoding
            except UnicodeDecodeError:
                continue
                
        return 'utf-8'  # Default fallback
    
    def extrair_csv(self, caminho_csv: str) -> Dict:
        """
        Extrai dados de arquivo CSV
        """
        resultado = {
            'dados': [],
            'metadados': {},
            'colunas': [],
            'estatisticas': {}
        }
        
        try:
            # Detectar encoding
            encoding = self.detectar_encoding(caminho_csv)
            logger.info(f"Usando encoding: {encoding}")
            
            # Ler com pandas para análise mais robusta
            try:
                df = pd.read_csv(caminho_csv, encoding=encoding)
                
                # Metadados básicos
                resultado['metadados'] = {
                    'encoding': encoding,
                    'num_linhas': len(df),
                    'num_colunas': len(df.columns),
                    'tamanho_arquivo': os.path.getsize(caminho_csv),
                    'colunas_com_valores_nulos': df.isnull().sum().to_dict(),
                    'tipos_dados': df.dtypes.astype(str).to_dict()
                }
                
                # Colunas
                resultado['colunas'] = df.columns.tolist()
                
                # Dados (converter para lista de dicionários)
                resultado['dados'] = df.to_dict('records')
                
                # Estatísticas básicas para colunas numéricas
                colunas_numericas = df.select_dtypes(include=['number']).columns
                if len(colunas_numericas) > 0:
                    resultado['estatisticas'] = df[colunas_numericas].describe().to_dict()
                
            except Exception as e:
                logger.warning(f"Erro com pandas, usando csv padrão: {e}")
                
                # Fallback: usar módulo csv padrão
                with open(caminho_csv, 'r', encoding=encoding, newline='') as f:
                    reader = csv.DictReader(f)
                    resultado['colunas'] = reader.fieldnames or []
                    resultado['dados'] = list(reader)
                    resultado['metadados'] = {
                        'encoding': encoding,
                        'num_linhas': len(resultado['dados']),
                        'num_colunas': len(resultado['colunas']),
                        'tamanho_arquivo': os.path.getsize(caminho_csv)
                    }
                    
        except Exception as e:
            logger.error(f"Erro ao extrair CSV {caminho_csv}: {e}")
            
        return resultado
    
    def extrair_xlsx(self, caminho_xlsx: str) -> Dict:
        """
        Extrai dados de arquivo XLSX
        """
        resultado = {
            'planilhas': {},
            'metadados': {}
        }
        
        try:
            # Carregar arquivo Excel
            excel_file = pd.ExcelFile(caminho_xlsx)
            
            # Metadados gerais
            resultado['metadados'] = {
                'num_planilhas': len(excel_file.sheet_names),
                'nomes_planilhas': excel_file.sheet_names,
                'tamanho_arquivo': os.path.getsize(caminho_xlsx)
            }
            
            # Processar cada planilha
            for nome_planilha in excel_file.sheet_names:
                try:
                    df = pd.read_excel(caminho_xlsx, sheet_name=nome_planilha)
                    
                    planilha_info = {
                        'dados': df.to_dict('records'),
                        'colunas': df.columns.tolist(),
                        'metadados': {
                            'num_linhas': len(df),
                            'num_colunas': len(df.columns),
                            'colunas_com_valores_nulos': df.isnull().sum().to_dict(),
                            'tipos_dados': df.dtypes.astype(str).to_dict()
                        },
                        'estatisticas': {}
                    }
                    
                    # Estatísticas para colunas numéricas
                    colunas_numericas = df.select_dtypes(include=['number']).columns
                    if len(colunas_numericas) > 0:
                        planilha_info['estatisticas'] = df[colunas_numericas].describe().to_dict()
                    
                    resultado['planilhas'][nome_planilha] = planilha_info
                    
                except Exception as e:
                    logger.error(f"Erro ao processar planilha {nome_planilha}: {e}")
                    
        except Exception as e:
            logger.error(f"Erro ao extrair XLSX {caminho_xlsx}: {e}")
            
        return resultado
    
    def processar_arquivo(self, caminho_arquivo: str, formato_saida: str = "json") -> bool:
        """
        Processa um arquivo CSV/XLSX específico
        
        Args:
            caminho_arquivo: Caminho para o arquivo CSV/XLSX
            formato_saida: 'txt', 'json' ou 'csv'
        """
        if not os.path.exists(caminho_arquivo):
            logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            return False
            
        nome_arquivo = Path(caminho_arquivo).stem
        extensao = Path(caminho_arquivo).suffix.lower()
        
        logger.info(f"Processando: {nome_arquivo}{extensao}")
        
        # Extrair dados conforme o tipo de arquivo
        if extensao == '.csv':
            dados = self.extrair_csv(caminho_arquivo)
        elif extensao in ['.xlsx', '.xls']:
            dados = self.extrair_xlsx(caminho_arquivo)
        else:
            logger.error(f"Formato não suportado: {extensao}")
            return False
        
        # Salvar conforme formato solicitado
        if formato_saida == "json":
            arquivo_saida = self.pasta_destino / f"{nome_arquivo}_dados.json"
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
                
        elif formato_saida == "csv":
            if extensao == '.csv':
                # Para CSV, criar versão limpa
                if dados['dados']:
                    arquivo_saida = self.pasta_destino / f"{nome_arquivo}_limpo.csv"
                    df = pd.DataFrame(dados['dados'])
                    df.to_csv(arquivo_saida, index=False, encoding='utf-8')
                    
            else:  # XLSX
                # Para XLSX, salvar cada planilha como CSV separado
                for nome_planilha, info_planilha in dados['planilhas'].items():
                    if info_planilha['dados']:
                        arquivo_saida = self.pasta_destino / f"{nome_arquivo}_{nome_planilha}.csv"
                        df = pd.DataFrame(info_planilha['dados'])
                        df.to_csv(arquivo_saida, index=False, encoding='utf-8')
                        
        elif formato_saida == "txt":
            arquivo_saida = self.pasta_destino / f"{nome_arquivo}_resumo.txt"
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(f"=== Resumo do arquivo: {nome_arquivo}{extensao} ===\n\n")
                
                if extensao == '.csv':
                    f.write(f"Tipo: CSV\n")
                    f.write(f"Linhas: {dados['metadados'].get('num_linhas', 0)}\n")
                    f.write(f"Colunas: {dados['metadados'].get('num_colunas', 0)}\n")
                    f.write(f"Encoding: {dados['metadados'].get('encoding', 'N/A')}\n\n")
                    f.write("Colunas:\n")
                    for col in dados['colunas']:
                        f.write(f"  - {col}\n")
                        
                else:  # XLSX
                    f.write(f"Tipo: XLSX\n")
                    f.write(f"Planilhas: {dados['metadados'].get('num_planilhas', 0)}\n\n")
                    
                    for nome_planilha, info in dados['planilhas'].items():
                        f.write(f"Planilha: {nome_planilha}\n")
                        f.write(f"  Linhas: {info['metadados']['num_linhas']}\n")
                        f.write(f"  Colunas: {info['metadados']['num_colunas']}\n")
                        f.write("  Colunas:\n")
                        for col in info['colunas']:
                            f.write(f"    - {col}\n")
                        f.write("\n")
        
        logger.info(f"Dados salvos em: {arquivo_saida}")
        return True
    
    def processar_pasta(self, formato_saida: str = "json") -> List[str]:
        """
        Processa todos os arquivos CSV/XLSX na pasta de origem
        """
        arquivos_processados = []
        
        if not self.pasta_origem.exists():
            logger.error(f"Pasta de origem não encontrada: {self.pasta_origem}")
            return arquivos_processados
            
        # Buscar todos os arquivos
        arquivos = (list(self.pasta_origem.glob("*.csv")) + 
                   list(self.pasta_origem.glob("*.xlsx")) +
                   list(self.pasta_origem.glob("*.xls")))
        
        if not arquivos:
            logger.warning(f"Nenhum arquivo CSV/XLSX encontrado em: {self.pasta_origem}")
            return arquivos_processados
            
        logger.info(f"Encontrados {len(arquivos)} arquivos CSV/XLSX")
        
        for arquivo_path in arquivos:
            try:
                if self.processar_arquivo(str(arquivo_path), formato_saida):
                    arquivos_processados.append(str(arquivo_path))
            except Exception as e:
                logger.error(f"Erro ao processar {arquivo_path}: {e}")
                
        return arquivos_processados

def main():
    """
    Função principal para execução do script
    """
    print("=== Extrator de Dados CSV/XLSX ===")
    print("1. Processar arquivo específico")
    print("2. Processar todos os CSV/XLSX da pasta")
    
    opcao = input("\nEscolha uma opção (1-2): ").strip()
    
    extrator = ExtratorCSVXLSX()
    
    if opcao == "1":
        caminho = input("Digite o caminho do arquivo CSV/XLSX: ").strip()
        formato = input("Formato de saída (txt/json/csv) [json]: ").strip() or "json"
        
        if extrator.processar_arquivo(caminho, formato):
            print("✅ Processamento concluído com sucesso!")
        else:
            print("❌ Erro no processamento.")
            
    elif opcao == "2":
        formato = input("Formato de saída (txt/json/csv) [json]: ").strip() or "json"
        
        processados = extrator.processar_pasta(formato)
        print(f"\n✅ {len(processados)} arquivos processados com sucesso!")
        
        for arquivo in processados:
            print(f"  - {os.path.basename(arquivo)}")
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()