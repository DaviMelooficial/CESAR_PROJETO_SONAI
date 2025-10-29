import pandas as pd
import json
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatamartGenerator:
    """Classe para gerar datamart em formato Parquet"""
    
    def __init__(self):
        self.pasta_processed = Path("../data/processed")
        self.pasta_datamart = Path("../data/datamart")
        self.pasta_raw = Path("../data/raw")
        
        # Criar pasta datamart se não existir
        self.pasta_datamart.mkdir(parents=True, exist_ok=True)
        
    def extrair_dados_primeiro(self):
        """Primeiro extrai dados se a pasta processed estiver vazia"""
        if not any(self.pasta_processed.glob("*.json")):
            logger.info("📂 Pasta processed vazia. Executando extração primeiro...")
            
            # Importar e executar o extrator principal
            import sys
            sys.path.append(str(Path(__file__).parent))
            
            try:
                from extrator_principal import main
                main()
                logger.info("✅ Extração concluída!")
            except Exception as e:
                logger.warning(f"⚠️ Erro na extração: {e}")
                self._criar_dados_exemplo()
    
    def _criar_dados_exemplo(self):
        """Cria dados de exemplo se não houver arquivos JSON"""
        logger.info("🎯 Criando dados de exemplo para demonstração...")
        
        # Dados de exemplo estruturados
        dados_exemplo = {
            "vendas_dados": {
                "dados": [
                    {"Data": "2024-01-15", "Produto": "Notebook", "Quantidade": 2, "Preco_Unitario": 3500.0, "Categoria": "Informática"},
                    {"Data": "2024-01-16", "Produto": "Mouse", "Quantidade": 5, "Preco_Unitario": 50.0, "Categoria": "Acessórios"},
                    {"Data": "2024-01-17", "Produto": "Monitor", "Quantidade": 1, "Preco_Unitario": 800.0, "Categoria": "Informática"},
                    {"Data": "2024-02-01", "Produto": "Teclado", "Quantidade": 3, "Preco_Unitario": 150.0, "Categoria": "Acessórios"},
                    {"Data": "2024-02-15", "Produto": "Notebook", "Quantidade": 1, "Preco_Unitario": 3500.0, "Categoria": "Informática"},
                    {"Data": "2024-03-01", "Produto": "Impressora", "Quantidade": 2, "Preco_Unitario": 400.0, "Categoria": "Escritório"},
                    {"Data": "2024-03-15", "Produto": "Mouse", "Quantidade": 8, "Preco_Unitario": 50.0, "Categoria": "Acessórios"},
                    {"Data": "2024-04-01", "Produto": "Monitor", "Quantidade": 3, "Preco_Unitario": 800.0, "Categoria": "Informática"},
                ],
                "metadados": {
                    "num_linhas": 8,
                    "num_colunas": 5,
                    "origem": "vendas_exemplo"
                }
            },
            "projetos_dados": {
                "dados": [
                    {"ID_Projeto": "P001", "Nome_Projeto": "Sistema ERP", "Status": "Concluído", "Orcamento": 50000.0, "Data_Inicio": "2024-01-01", "Data_Fim": "2024-06-30"},
                    {"ID_Projeto": "P002", "Nome_Projeto": "App Mobile", "Status": "Em Andamento", "Orcamento": 30000.0, "Data_Inicio": "2024-03-01", "Data_Fim": "2024-12-31"},
                    {"ID_Projeto": "P003", "Nome_Projeto": "Website", "Status": "Concluído", "Orcamento": 15000.0, "Data_Inicio": "2024-02-01", "Data_Fim": "2024-05-31"},
                    {"ID_Projeto": "P004", "Nome_Projeto": "Dashboard BI", "Status": "Planejado", "Orcamento": 25000.0, "Data_Inicio": "2024-07-01", "Data_Fim": "2024-11-30"},
                    {"ID_Projeto": "P005", "Nome_Projeto": "Automação", "Status": "Em Andamento", "Orcamento": 40000.0, "Data_Inicio": "2024-04-01", "Data_Fim": "2024-10-31"},
                ],
                "metadados": {
                    "num_linhas": 5,
                    "num_colunas": 6,
                    "origem": "projetos_exemplo"
                }
            }
        }
        
        # Salvar dados de exemplo como JSON
        for nome, dados in dados_exemplo.items():
            arquivo_json = self.pasta_processed / f"{nome}.json"
            with open(arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            logger.info(f"📄 Criado: {arquivo_json}")
    
    def processar_arquivos_json(self):
        """Processa todos os arquivos JSON e converte para Parquet"""
        logger.info("🔄 Iniciando processamento dos arquivos JSON...")
        
        arquivos_json = list(self.pasta_processed.glob("*.json"))
        
        if not arquivos_json:
            logger.warning("❌ Nenhum arquivo JSON encontrado!")
            return
        
        datasets_criados = []
        
        for arquivo_json in arquivos_json:
            try:
                logger.info(f"📊 Processando: {arquivo_json.name}")
                
                # Carregar JSON
                with open(arquivo_json, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                
                # Processar baseado na estrutura
                if 'dados' in dados_json:
                    # Estrutura padrão do extrator
                    df = pd.DataFrame(dados_json['dados'])
                    nome_base = arquivo_json.stem
                    
                    # Adicionar metadados como colunas
                    if 'metadados' in dados_json:
                        df['arquivo_origem'] = nome_base
                        df['data_processamento'] = datetime.now()
                    
                elif isinstance(dados_json, list):
                    # JSON como lista direta
                    df = pd.DataFrame(dados_json)
                    nome_base = arquivo_json.stem
                else:
                    # Tentar converter estrutura complexa
                    df = pd.json_normalize(dados_json)
                    nome_base = arquivo_json.stem
                
                # Limpar e otimizar tipos de dados
                df = self._otimizar_dataframe(df)
                
                # Salvar como Parquet
                arquivo_parquet = self.pasta_datamart / f"{nome_base}.parquet"
                df.to_parquet(arquivo_parquet, engine='pyarrow', compression='snappy')
                
                logger.info(f"✅ Criado: {arquivo_parquet} ({len(df)} linhas)")
                datasets_criados.append({
                    'arquivo': nome_base,
                    'linhas': len(df),
                    'colunas': len(df.columns),
                    'tamanho_mb': arquivo_parquet.stat().st_size / 1024 / 1024
                })
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {arquivo_json}: {e}")
        
        return datasets_criados
    
    def _otimizar_dataframe(self, df):
        """Otimiza tipos de dados do DataFrame para Parquet"""
        
        for col in df.columns:
            # Converter datas
            if 'data' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
            
            # Otimizar tipos numéricos
            elif df[col].dtype == 'float64':
                if df[col].notna().all() and (df[col] % 1 == 0).all():
                    df[col] = df[col].astype('int64')
                else:
                    df[col] = df[col].astype('float32')
            
            elif df[col].dtype == 'int64':
                max_val = df[col].max()
                min_val = df[col].min()
                
                if min_val >= 0 and max_val < 256:
                    df[col] = df[col].astype('uint8')
                elif min_val >= -128 and max_val < 128:
                    df[col] = df[col].astype('int8')
                elif min_val >= -32768 and max_val < 32768:
                    df[col] = df[col].astype('int16')
                elif min_val >= -2147483648 and max_val < 2147483648:
                    df[col] = df[col].astype('int32')
            
            # Otimizar strings categóricas
            elif df[col].dtype == 'object':
                if df[col].nunique() < len(df) * 0.5:  # Se menos de 50% únicos
                    df[col] = df[col].astype('category')
        
        return df
    
    def criar_dataset_consolidado(self):
        """Cria um dataset consolidado combinando múltiplas fontes"""
        logger.info("📋 Criando dataset consolidado...")
        
        try:
            # Lista todos os parquets
            arquivos_parquet = list(self.pasta_datamart.glob("*.parquet"))
            
            if not arquivos_parquet:
                logger.warning("❌ Nenhum arquivo Parquet encontrado para consolidar!")
                return
            
            datasets_info = []
            
            for arquivo in arquivos_parquet:
                df = pd.read_parquet(arquivo)
                
                info = {
                    'dataset': arquivo.stem,
                    'linhas': len(df),
                    'colunas': len(df.columns),
                    'colunas_nomes': list(df.columns),
                    'tipos_dados': df.dtypes.astype(str).to_dict(),
                    'memoria_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'data_criacao': datetime.now()
                }
                datasets_info.append(info)
            
            # Criar DataFrame de metadados
            df_metadados = pd.DataFrame(datasets_info)
            
            # Salvar metadados
            arquivo_metadados = self.pasta_datamart / "metadados_datamart.parquet"
            df_metadados.to_parquet(arquivo_metadados, engine='pyarrow')
            
            logger.info(f"✅ Dataset consolidado criado: {arquivo_metadados}")
            
            return df_metadados
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar dataset consolidado: {e}")
    
    def gerar_relatorio_datamart(self):
        """Gera relatório do datamart criado"""
        logger.info("\n" + "="*60)
        logger.info("📊 RELATÓRIO DO DATAMART GERADO")
        logger.info("="*60)
        
        arquivos = list(self.pasta_datamart.glob("*.parquet"))
        
        if not arquivos:
            logger.warning("❌ Nenhum arquivo Parquet encontrado!")
            return
        
        total_size = 0
        total_records = 0
        
        logger.info(f"\n📁 Localização: {self.pasta_datamart}")
        logger.info(f"📈 Total de arquivos: {len(arquivos)}")
        
        for arquivo in arquivos:
            try:
                df = pd.read_parquet(arquivo)
                size_mb = arquivo.stat().st_size / 1024 / 1024
                total_size += size_mb
                total_records += len(df)
                
                logger.info(f"\n📄 {arquivo.name}:")
                logger.info(f"   • Registros: {len(df):,}")
                logger.info(f"   • Colunas: {len(df.columns)}")
                logger.info(f"   • Tamanho: {size_mb:.2f} MB")
                logger.info(f"   • Colunas: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao ler {arquivo}: {e}")
        
        logger.info(f"\n📊 RESUMO TOTAL:")
        logger.info(f"   • Total de registros: {total_records:,}")
        logger.info(f"   • Tamanho total: {total_size:.2f} MB")
        logger.info(f"   • Compressão: Snappy")
        logger.info(f"   • Formato: Parquet (Apache Arrow)")
        
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info(f"   1. Use os arquivos .parquet no dashboard Streamlit")
        logger.info(f"   2. Importe com: pd.read_parquet('data/datamart/arquivo.parquet')")
        logger.info(f"   3. Localização: {self.pasta_datamart.absolute()}")
        
        return {
            'total_arquivos': len(arquivos),
            'total_registros': total_records,
            'tamanho_total_mb': total_size,
            'pasta': str(self.pasta_datamart.absolute())
        }

def main():
    """Função principal"""
    print("🚀 GERADOR DE DATAMART - STREAMLIT")
    print("="*50)
    
    generator = DatamartGenerator()
    
    # 1. Verificar e extrair dados se necessário
    generator.extrair_dados_primeiro()
    
    # 2. Processar JSONs para Parquet
    datasets = generator.processar_arquivos_json()
    
    # 3. Criar dataset consolidado
    generator.criar_dataset_consolidado()
    
    # 4. Gerar relatório
    relatorio = generator.gerar_relatorio_datamart()
    
    print(f"\n✅ Datamart gerado com sucesso!")
    print(f"📁 Localização: {relatorio['pasta']}")
    print(f"📊 {relatorio['total_arquivos']} arquivos Parquet criados")
    print(f"🎯 Pronto para uso com Streamlit!")

if __name__ == "__main__":
    main()