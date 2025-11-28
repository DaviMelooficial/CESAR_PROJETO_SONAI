import sqlite3
import hashlib
import os
from pathlib import Path

class AuthDB:
    """Gerenciador de autenticação e banco de dados de usuários"""
    
    def __init__(self, db_path="users.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria tabelas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL,
                email TEXT,
                nivel_acesso TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP
            )
        ''')
        
        # Criar tabela de logs de acesso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_acesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acao TEXT NOT NULL,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Criar usuários padrão se não existirem
        self.criar_usuarios_padrao()
    
    def hash_password(self, password):
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def criar_usuarios_padrao(self):
        """Cria usuários padrão para cada nível de acesso"""
        usuarios_padrao = [
            {
                'username': 'admin',
                'password': 'admin123',
                'nome_completo': 'Administrador',
                'email': 'admin@mcsonae.com',
                'nivel_acesso': 'Estratégico'
            },
            {
                'username': 'gerente',
                'password': 'gerente123',
                'nome_completo': 'Gerente de Projetos',
                'email': 'gerente@mcsonae.com',
                'nivel_acesso': 'Tático'
            },
            {
                'username': 'operador',
                'password': 'operador123',
                'nome_completo': 'Operador de Sistema',
                'email': 'operador@mcsonae.com',
                'nivel_acesso': 'Operacional'
            }
        ]
        
        for usuario in usuarios_padrao:
            try:
                self.criar_usuario(
                    username=usuario['username'],
                    password=usuario['password'],
                    nome_completo=usuario['nome_completo'],
                    email=usuario['email'],
                    nivel_acesso=usuario['nivel_acesso']
                )
            except:
                pass  # Usuário já existe
    
    def criar_usuario(self, username, password, nome_completo, email, nivel_acesso):
        """Cria um novo usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nome_completo, email, nivel_acesso)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, nome_completo, email, nivel_acesso))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def autenticar(self, username, password):
        """Autentica um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, username, nome_completo, email, nivel_acesso, ativo
            FROM usuarios
            WHERE username = ? AND password_hash = ? AND ativo = 1
        ''', (username, password_hash))
        
        usuario = cursor.fetchone()
        
        if usuario:
            # Atualizar último login
            cursor.execute('''
                UPDATE usuarios
                SET ultimo_login = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))
            
            # Registrar log de acesso
            cursor.execute('''
                INSERT INTO logs_acesso (username, acao)
                VALUES (?, 'LOGIN')
            ''', (username,))
            
            conn.commit()
            
            # Retornar dados do usuário
            return {
                'id': usuario[0],
                'username': usuario[1],
                'nome_completo': usuario[2],
                'email': usuario[3],
                'nivel_acesso': usuario[4],
                'ativo': usuario[5]
            }
        
        conn.close()
        return None
    
    def listar_usuarios(self):
        """Lista todos os usuários"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nome_completo, email, nivel_acesso, ativo, data_criacao, ultimo_login
            FROM usuarios
            ORDER BY id
        ''')
        
        usuarios = cursor.fetchall()
        conn.close()
        
        return usuarios
    
    def alterar_senha(self, username, senha_antiga, senha_nova):
        """Altera a senha de um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar senha antiga
        password_hash_antiga = self.hash_password(senha_antiga)
        cursor.execute('''
            SELECT id FROM usuarios
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash_antiga))
        
        if cursor.fetchone():
            # Atualizar senha
            password_hash_nova = self.hash_password(senha_nova)
            cursor.execute('''
                UPDATE usuarios
                SET password_hash = ?
                WHERE username = ?
            ''', (password_hash_nova, username))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def desativar_usuario(self, username):
        """Desativa um usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE usuarios
            SET ativo = 0
            WHERE username = ?
        ''', (username,))
        
        conn.commit()
        conn.close()
    
    def registrar_acao(self, username, acao):
        """Registra uma ação do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs_acesso (username, acao)
            VALUES (?, ?)
        ''', (username, acao))
        
        conn.commit()
        conn.close()
