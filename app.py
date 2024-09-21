from flask import Flask, jsonify, request
import csv

app = Flask(__name__)

# Função para ler o arquivo CSV
def read_csv():
    data = []
    try:
        with open('spotify_artist_data.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')  # Define o delimitador como vírgula
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        # Se o arquivo não existir, retorna uma lista vazia
        data = []
    return data

# Função para salvar os dados no CSV
def write_csv(data):
    if not data:
        return
    fieldnames = data[0].keys()
    with open('spotify_artist_data.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Função para gerar o próximo índice
def gerar_proximo_indice(data):
    if not data:
        return 1
    # Encontra o maior índice existente e retorna o próximo valor
    indices_existentes = [int(item['Index']) for item in data if 'Index' in item]
    return max(indices_existentes) + 1 if indices_existentes else 1

# Rota para consultar todos os dados
@app.route('/data', methods=['GET'])
def get_data():
    data = read_csv()
    return jsonify(data)

# Rota para consultar um artista específico pelo nome
@app.route('/data/artist/<nome_artista>', methods=['GET'])
def get_data_artista(nome_artista):
    data = read_csv()
    resultado = next((item for item in data if item['Artist Name'].lower() == nome_artista.lower()), None)
    if resultado:
        return jsonify(resultado)
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para consultar um artista específico pelo índice
@app.route('/data/index/<int:artista_index>', methods=['GET'])
def get_data_artista_por_index(artista_index):
    data = read_csv()
    resultado = next((item for item in data if int(item['Index']) == artista_index), None)
    if resultado:
        return jsonify(resultado)
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para modificar dados por "Artist Name"
@app.route('/data/update/<nome_artista>', methods=['PUT'])
def update_data(nome_artista):
    data = read_csv()
    updated = False
    for item in data:
        if item.get('Artist Name') and item['Artist Name'].lower() == nome_artista.lower():
            for key, value in request.json.items():
                if key in item:  # Atualiza apenas as colunas existentes
                    item[key] = value
            updated = True
            break

    if updated:
        write_csv(data)
        return jsonify({"mensagem": f"Dados do artista '{nome_artista}' atualizados com sucesso!"})
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para modificar dados por "Index"
@app.route('/data/update/index/<int:artista_index>', methods=['PUT'])
def update_data_por_index(artista_index):
    data = read_csv()
    updated = False
    for item in data:
        if int(item['Index']) == artista_index:
            for key, value in request.json.items():
                if key in item:  # Atualiza apenas as colunas existentes
                    item[key] = value
            updated = True
            break

    if updated:
        write_csv(data)
        return jsonify({"mensagem": f"Dados do artista com índice '{artista_index}' atualizados com sucesso!"})
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para deletar um artista por "Artist Name"
@app.route('/data/delete/<nome_artista>', methods=['DELETE'])
def delete_artist(nome_artista):
    data = read_csv()
    original_length = len(data)

    # Remove o artista correspondente ao nome fornecido, verificando se 'Artist Name' está presente e não é None
    data = [item for item in data if item.get('Artist Name') and item['Artist Name'].lower() != nome_artista.lower()]

    if len(data) < original_length:
        write_csv(data)
        return jsonify({"mensagem": f"Artista '{nome_artista}' deletado com sucesso!"})
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para deletar um artista por "Index"
@app.route('/data/delete/index/<int:artista_index>', methods=['DELETE'])
def delete_artist_por_index(artista_index):
    data = read_csv()
    original_length = len(data)

    # Remove o artista correspondente ao índice fornecido
    data = [item for item in data if int(item['Index']) != artista_index]

    if len(data) < original_length:
        write_csv(data)
        return jsonify({"mensagem": f"Artista com índice '{artista_index}' deletado com sucesso!"})
    else:
        return jsonify({"erro": "Artista não encontrado"}), 404

# Rota para adicionar um novo artista
@app.route('/data/add', methods=['POST'])
def adicionar_artista():
    novo_artista = request.json
    data = read_csv()

    # Verifica se o artista já existe
    if any(artista['Artist Name'].lower() == novo_artista['Artist Name'].lower() for artista in data):
        return jsonify({"erro": "Artista já existe!"}), 400
    
    # Gera um novo índice automaticamente
    novo_indice = gerar_proximo_indice(data)
    novo_artista['Index'] = str(novo_indice)  # Adiciona o índice como string

    data.append(novo_artista)
    write_csv(data)
    return jsonify(novo_artista), 201

if __name__ == '__main__':
    app.run(port=8000, host='localhost', debug=True)
