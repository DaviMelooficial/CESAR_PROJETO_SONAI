"""
Script Principal - Extrator Universal de Documentos
Unifica todos os extratores (PDF, DOC, CSV/XLSX) em uma única interface
Autor: Sistema de Análise e Visualização
Data: Setembro 2025
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Dict
import argparse
import datetime

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar os extratores (com tratamento de erro para dependências)
try:
    from extrator_pdf import ExtratorPDF
    PDF_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️ Extrator PDF não disponível: {e}")
    PDF_DISPONIVEL = False

try:
    from extrator_doc import ExtratorDOC
    DOC_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️ Extrator DOC não disponível: {e}")
    DOC_DISPONIVEL = False

try:
    from extrator_csv_xlsx import ExtratorCSVXLSX
    CSV_XLSX_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️ Extrator CSV/XLSX não disponível: {e}")
    CSV_XLSX_DISPONIVEL = False

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtratorUniversal:
    """
    Classe principal que unifica todos os extratores
    """
    
    def __init__(self, pasta_origem: str = "../data/raw", pasta_destino: str = "../data/processed"):
        self.pasta_origem = Path(pasta_origem)
        self.pasta_destino = Path(pasta_destino)
        
        # Criar pastas se não existirem
        self.pasta_origem.mkdir(parents=True, exist_ok=True)
        self.pasta_destino.mkdir(parents=True, exist_ok=True)
        
        # Inicializar extratores disponíveis
        self.extratores = {}
        
        if PDF_DISPONIVEL:
            self.extratores['pdf'] = ExtratorPDF(pasta_origem, pasta_destino)
            
        if DOC_DISPONIVEL:
            self.extratores['doc'] = ExtratorDOC(pasta_origem, pasta_destino)
            
        if CSV_XLSX_DISPONIVEL:
            self.extratores['csv_xlsx'] = ExtratorCSVXLSX(pasta_origem, pasta_destino)
    
    def listar_arquivos_disponiveis(self) -> Dict[str, List[str]]:
        """
        Lista todos os arquivos disponíveis na pasta de origem por tipo
        """
        arquivos_por_tipo = {
            'pdf': [],
            'doc': [],
            'csv': [],
            'xlsx': []
        }
        
        if not self.pasta_origem.exists():
            logger.warning(f"Pasta de origem não encontrada: {self.pasta_origem}")
            return arquivos_por_tipo
        
        # Buscar arquivos por extensão
        for arquivo in self.pasta_origem.rglob("*"):
            if arquivo.is_file():
                extensao = arquivo.suffix.lower()
                
                if extensao == '.pdf':
                    arquivos_por_tipo['pdf'].append(str(arquivo))
                elif extensao in ['.doc', '.docx']:
                    arquivos_por_tipo['doc'].append(str(arquivo))
                elif extensao == '.csv':
                    arquivos_por_tipo['csv'].append(str(arquivo))
                elif extensao in ['.xlsx', '.xls']:
                    arquivos_por_tipo['xlsx'].append(str(arquivo))
        
        return arquivos_por_tipo
    
    def processar_todos_arquivos(self, formato_saida: str = "json") -> Dict[str, List[str]]:
        """
        Processa todos os arquivos disponíveis
        """
        resultado = {
            'processados': [],
            'erros': [],
            'nao_suportados': []
        }
        
        arquivos = self.listar_arquivos_disponiveis()
        total_arquivos = sum(len(lista) for lista in arquivos.values())
        
        if total_arquivos == 0:
            logger.warning("Nenhum arquivo encontrado para processar")
            return resultado
        
        logger.info(f"Processando {total_arquivos} arquivos...")
        
        # Processar PDFs
        if arquivos['pdf'] and 'pdf' in self.extratores:
            logger.info(f"Processando {len(arquivos['pdf'])} arquivos PDF...")
            for pdf_path in arquivos['pdf']:
                try:
                    if self.extratores['pdf'].processar_arquivo(pdf_path, formato_saida):
                        resultado['processados'].append(pdf_path)
                    else:
                        resultado['erros'].append(pdf_path)
                except Exception as e:
                    logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
                    resultado['erros'].append(pdf_path)
        elif arquivos['pdf']:
            resultado['nao_suportados'].extend(arquivos['pdf'])
        
        # Processar DOCs
        if arquivos['doc'] and 'doc' in self.extratores:
            logger.info(f"Processando {len(arquivos['doc'])} arquivos DOC/DOCX...")
            for doc_path in arquivos['doc']:
                try:
                    if self.extratores['doc'].processar_arquivo(doc_path, formato_saida):
                        resultado['processados'].append(doc_path)
                    else:
                        resultado['erros'].append(doc_path)
                except Exception as e:
                    logger.error(f"Erro ao processar DOC {doc_path}: {e}")
                    resultado['erros'].append(doc_path)
        elif arquivos['doc']:
            resultado['nao_suportados'].extend(arquivos['doc'])
        
        # Processar CSVs e XLSXs
        arquivos_csv_xlsx = arquivos['csv'] + arquivos['xlsx']
        if arquivos_csv_xlsx and 'csv_xlsx' in self.extratores:
            logger.info(f"Processando {len(arquivos_csv_xlsx)} arquivos CSV/XLSX...")
            for arquivo_path in arquivos_csv_xlsx:
                try:
                    if self.extratores['csv_xlsx'].processar_arquivo(arquivo_path, formato_saida):
                        resultado['processados'].append(arquivo_path)
                    else:
                        resultado['erros'].append(arquivo_path)
                except Exception as e:
                    logger.error(f"Erro ao processar CSV/XLSX {arquivo_path}: {e}")
                    resultado['erros'].append(arquivo_path)
        elif arquivos_csv_xlsx:
            resultado['nao_suportados'].extend(arquivos_csv_xlsx)
        
        return resultado
    
    def gerar_relatorio(self, resultado: Dict[str, List[str]]) -> str:
        """
        Gera um relatório do processamento
        """
        relatorio = f"""
=== RELATÓRIO DE PROCESSAMENTO ===
Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Arquivos processados com sucesso: {len(resultado['processados'])}
❌ Arquivos com erro: {len(resultado['erros'])}
⚠️ Arquivos não suportados: {len(resultado['nao_suportados'])}

PROCESSADOS:
"""
        
        for arquivo in resultado['processados']:
            relatorio += f"  ✅ {os.path.basename(arquivo)}\n"
        
        if resultado['erros']:
            relatorio += "\nERROS:\n"
            for arquivo in resultado['erros']:
                relatorio += f"  ❌ {os.path.basename(arquivo)}\n"
        
        if resultado['nao_suportados']:
            relatorio += "\nNÃO SUPORTADOS:\n"
            for arquivo in resultado['nao_suportados']:
                relatorio += f"  ⚠️ {os.path.basename(arquivo)}\n"
        
        relatorio += f"\nExtratores disponíveis: {', '.join(self.extratores.keys())}\n"
        
        return relatorio
    
    def exibir_status(self):
        """
        Exibe o status dos extratores e arquivos disponíveis
        """
        print("=== STATUS DO SISTEMA ===")
        print(f"Pasta origem: {self.pasta_origem}")
        print(f"Pasta destino: {self.pasta_destino}")
        print()
        
        print("Extratores disponíveis:")
        print(f"  📄 PDF: {'✅' if PDF_DISPONIVEL else '❌'}")
        print(f"  📝 DOC/DOCX: {'✅' if DOC_DISPONIVEL else '❌'}")
        print(f"  📊 CSV/XLSX: {'✅' if CSV_XLSX_DISPONIVEL else '❌'}")
        print()
        
        arquivos = self.listar_arquivos_disponiveis()
        print("Arquivos encontrados:")
        for tipo, lista in arquivos.items():
            print(f"  {tipo.upper()}: {len(lista)} arquivo(s)")
            for arquivo in lista[:3]:  # Mostrar apenas os primeiros 3
                print(f"    - {os.path.basename(arquivo)}")
            if len(lista) > 3:
                print(f"    ... e mais {len(lista) - 3} arquivo(s)")

def main():
    """
    Função principal com interface de linha de comando
    """
    parser = argparse.ArgumentParser(description="Extrator Universal de Documentos")
    parser.add_argument("--origem", default="../data/raw", help="Pasta de origem dos arquivos")
    parser.add_argument("--destino", default="../data/processed", help="Pasta de destino dos dados extraídos")
    parser.add_argument("--formato", choices=['txt', 'json', 'csv'], default='json', help="Formato de saída")
    parser.add_argument("--arquivo", help="Processar arquivo específico")
    parser.add_argument("--todos", action='store_true', help="Processar todos os arquivos da pasta")
    parser.add_argument("--status", action='store_true', help="Mostrar status do sistema")
    parser.add_argument("--relatorio", help="Salvar relatório em arquivo")
    
    args = parser.parse_args()
    
    # Criar extrator
    extrator = ExtratorUniversal(args.origem, args.destino)
    
    if args.status:
        extrator.exibir_status()
        return
    
    if args.arquivo:
        # Processar arquivo específico
        arquivo_path = Path(args.arquivo)
        extensao = arquivo_path.suffix.lower()
        
        print(f"Processando arquivo: {arquivo_path.name}")
        
        sucesso = False
        if extensao == '.pdf' and 'pdf' in extrator.extratores:
            sucesso = extrator.extratores['pdf'].processar_arquivo(str(arquivo_path), args.formato)
        elif extensao in ['.doc', '.docx'] and 'doc' in extrator.extratores:
            sucesso = extrator.extratores['doc'].processar_arquivo(str(arquivo_path), args.formato)
        elif extensao in ['.csv', '.xlsx', '.xls'] and 'csv_xlsx' in extrator.extratores:
            sucesso = extrator.extratores['csv_xlsx'].processar_arquivo(str(arquivo_path), args.formato)
        else:
            print(f"❌ Formato {extensao} não suportado ou extrator não disponível")
            return
        
        if sucesso:
            print("✅ Processamento concluído com sucesso!")
        else:
            print("❌ Erro no processamento.")
            
    elif args.todos:
        # Processar todos os arquivos
        print("Processando todos os arquivos...")
        resultado = extrator.processar_todos_arquivos(args.formato)
        
        relatorio = extrator.gerar_relatorio(resultado)
        print(relatorio)
        
        # Salvar relatório se solicitado
        if args.relatorio:
            with open(args.relatorio, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            print(f"📄 Relatório salvo em: {args.relatorio}")
    
    else:
        # Interface interativa
        print("=== Extrator Universal de Documentos ===")
        print("1. Mostrar status do sistema")
        print("2. Processar arquivo específico")
        print("3. Processar todos os arquivos")
        print("4. Sair")
        
        while True:
            opcao = input("\nEscolha uma opção (1-4): ").strip()
            
            if opcao == "1":
                extrator.exibir_status()
                
            elif opcao == "2":
                caminho = input("Digite o caminho do arquivo: ").strip()
                formato = input("Formato de saída (txt/json/csv) [json]: ").strip() or "json"
                
                if os.path.exists(caminho):
                    # Determinar tipo e processar
                    arquivo_path = Path(caminho)
                    extensao = arquivo_path.suffix.lower()
                    
                    sucesso = False
                    if extensao == '.pdf' and 'pdf' in extrator.extratores:
                        sucesso = extrator.extratores['pdf'].processar_arquivo(caminho, formato)
                    elif extensao in ['.doc', '.docx'] and 'doc' in extrator.extratores:
                        sucesso = extrator.extratores['doc'].processar_arquivo(caminho, formato)
                    elif extensao in ['.csv', '.xlsx', '.xls'] and 'csv_xlsx' in extrator.extratores:
                        sucesso = extrator.extratores['csv_xlsx'].processar_arquivo(caminho, formato)
                    else:
                        print(f"❌ Formato {extensao} não suportado")
                        continue
                    
                    if sucesso:
                        print("✅ Processamento concluído com sucesso!")
                    else:
                        print("❌ Erro no processamento.")
                else:
                    print("❌ Arquivo não encontrado!")
                    
            elif opcao == "3":
                formato = input("Formato de saída (txt/json/csv) [json]: ").strip() or "json"
                
                resultado = extrator.processar_todos_arquivos(formato)
                relatorio = extrator.gerar_relatorio(resultado)
                print(relatorio)
                
            elif opcao == "4":
                print("👋 Até mais!")
                break
                
            else:
                print("❌ Opção inválida!")

if __name__ == "__main__":
    main()