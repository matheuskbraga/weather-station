from flask import Flask, render_template, request
import sqlite3
import datetime

app = Flask(__name__)

# Configuração do Nome do Banco de Dados
DB_NAME = "dados_estacao.db"

# Função para iniciar o banco de dados (Cria a tabela se não existir)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Criamos uma tabela com id, data, temperatura e umidade
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            temperatura REAL,
            umidade REAL
        )
    ''')
    conn.commit()
    conn.close()

# ROTA 1: Visualizar o Site (O que você vê)
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Pega as últimas 10 leituras (da mais recente para a mais antiga)
    cursor.execute("SELECT * FROM leituras ORDER BY id DESC LIMIT 10")
    dados = cursor.fetchall()
    
    # Pega apenas a leitura mais recente para destacar no topo do site
    ultima_leitura = dados[0] if dados else None
    
    conn.close()
    
    # Envia os dados para o HTML
    return render_template('index.html', leituras=dados, destaque=ultima_leitura)

# ROTA 2: Receber Dados (O que o Arduino vai usar)
@app.route('/api/gravar', methods=['GET'])
def gravar():
    # Pega os dados da URL (Ex: ?temp=25&umid=60)
    temp = request.args.get('temp')
    umid = request.args.get('umid')
    
    if temp and umid:
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leituras (data_hora, temperatura, umidade) VALUES (?, ?, ?)", 
                       (data_atual, temp, umid))
        conn.commit()
        conn.close()
        return "Dados salvos com sucesso!"
    else:
        return "Erro: Faltam dados (temp ou umid)"

if __name__ == '__main__':
    init_db() # Garante que o banco existe antes de rodar
    # Debug=True faz o site atualizar sozinho quando você mexe no código
    app.run(host='0.0.0.0', port=5000, debug=True)