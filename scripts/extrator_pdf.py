import os
import json
import csv
from typing import List, Dict, Optional
import PyPDF2
import pdfplumber
from pathlib import Path
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtratorPDF:
    """
    Classe para extrair texto e dados de arquivos PDF
    """
    
    def __init__(self, pasta_origem: str = "../data/raw", pasta_destino: str = "../data/processed"):
        self.pasta_origem = Path(pasta_origem)
        self.pasta_destino = Path(pasta_destino)
        
        # Criar pasta de destino se não existir
        self.pasta_destino.mkdir(parents=True, exist_ok=True)
        
    def extrair_texto_pypdf2(self, caminho_pdf: str) -> str:
        """
        Extrai texto usando PyPDF2
        """
        try:
            with open(caminho_pdf, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                texto_completo = ""
                
                for pagina_num in range(len(leitor.pages)):
                    pagina = leitor.pages[pagina_num]
                    texto_completo += pagina.extract_text() + "\n"
                    
                return texto_completo
        except Exception as e:
            logger.error(f"Erro ao extrair texto com PyPDF2 de {caminho_pdf}: {e}")
            return ""
    
    def extrair_texto_pdfplumber(self, caminho_pdf: str) -> Dict:
        """
        Extrai texto e tabelas usando pdfplumber (mais preciso)
        """
        resultado = {
            'texto': "",
            'tabelas': [],
            'metadados': {}
        }
        
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                # Metadados do PDF
                resultado['metadados'] = {
                    'num_paginas': len(pdf.pages),
                    'metadata': pdf.metadata if pdf.metadata else {}
                }
                
                # Extrair texto de cada página
                texto_completo = ""
                for i, pagina in enumerate(pdf.pages):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"--- Página {i+1} ---\n{texto_pagina}\n"
                    
                    # Extrair tabelas se existirem
                    tabelas_pagina = pagina.extract_tables()
                    if tabelas_pagina:
                        for j, tabela in enumerate(tabelas_pagina):
                            resultado['tabelas'].append({
                                'pagina': i+1,
                                'tabela_num': j+1,
                                'dados': tabela
                            })
                
                resultado['texto'] = texto_completo
                
        except Exception as e:
            logger.error(f"Erro ao extrair dados com pdfplumber de {caminho_pdf}: {e}")
            
        return resultado
    
    def processar_arquivo(self, caminho_pdf: str, formato_saida: str = "txt") -> bool:
        """
        Processa um arquivo PDF específico
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            formato_saida: 'txt', 'json' ou 'csv'
        """
        if not os.path.exists(caminho_pdf):
            logger.error(f"Arquivo não encontrado: {caminho_pdf}")
            return False
            
        nome_arquivo = Path(caminho_pdf).stem
        logger.info(f"Processando: {nome_arquivo}")
        
        # Extrair dados
        dados = self.extrair_texto_pdfplumber(caminho_pdf)
        
        if not dados['texto'].strip():
            # Fallback para PyPDF2 se pdfplumber falhar
            logger.warning("pdfplumber não conseguiu extrair texto, tentando PyPDF2...")
            texto_fallback = self.extrair_texto_pypdf2(caminho_pdf)
            dados['texto'] = texto_fallback
        
        # Salvar conforme formato solicitado
        if formato_saida == "txt":
            arquivo_saida = self.pasta_destino / f"{nome_arquivo}_extraido.txt"
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(dados['texto'])
                
        elif formato_saida == "json":
            arquivo_saida = self.pasta_destino / f"{nome_arquivo}_dados.json"
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                
        elif formato_saida == "csv":
            # Salvar texto como CSV (uma linha por parágrafo)
            arquivo_saida = self.pasta_destino / f"{nome_arquivo}_texto.csv"
            paragrafos = [p.strip() for p in dados['texto'].split('\n') if p.strip()]
            
            with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['pagina', 'paragrafo', 'texto'])
                for i, paragrafo in enumerate(paragrafos, 1):
                    writer.writerow([1, i, paragrafo])
            
            # Salvar tabelas separadamente se existirem
            if dados['tabelas']:
                for tab_info in dados['tabelas']:
                    arquivo_tabela = self.pasta_destino / f"{nome_arquivo}_tabela_p{tab_info['pagina']}_t{tab_info['tabela_num']}.csv"
                    with open(arquivo_tabela, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(tab_info['dados'])
        
        logger.info(f"Dados salvos em: {arquivo_saida}")
        return True
    
    def processar_pasta(self, formato_saida: str = "json") -> List[str]:
        """
        Processa todos os PDFs na pasta de origem
        """
        pdfs_processados = []
        
        if not self.pasta_origem.exists():
            logger.error(f"Pasta de origem não encontrada: {self.pasta_origem}")
            return pdfs_processados
            
        # Buscar todos os PDFs
        arquivos_pdf = list(self.pasta_origem.glob("*.pdf"))
        
        if not arquivos_pdf:
            logger.warning(f"Nenhum arquivo PDF encontrado em: {self.pasta_origem}")
            return pdfs_processados
            
        logger.info(f"Encontrados {len(arquivos_pdf)} arquivos PDF")
        
        for pdf_path in arquivos_pdf:
            try:
                if self.processar_arquivo(str(pdf_path), formato_saida):
                    pdfs_processados.append(str(pdf_path))
            except Exception as e:
                logger.error(f"Erro ao processar {pdf_path}: {e}")
                
        return pdfs_processados

def main():
    """
    Função principal para execução do script
    """
    print("=== Extrator de Dados PDF ===")
    print("1. Processar arquivo específico")
    print("2. Processar todos os PDFs da pasta")
    
    opcao = input("\nEscolha uma opção (1-2): ").strip()
    
    extrator = ExtratorPDF()
    
    if opcao == "1":
        caminho = input("Digite o caminho do arquivo PDF: ").strip()
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