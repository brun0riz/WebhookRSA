from flask import Flask, json, request, jsonify, render_template
from RSA.rsa import encript_message, decript_message
from config import Config
import requests

app_a = Flask(__name__)
APP_B_URL = "http://127.0.0.1:5001/receive_from_a"

messages_a_to_b = []
messages_received_from_b = []

def string_para_inteiro(texto):
    print("Texto:", texto)
    return int.from_bytes(texto.encode('utf-8'), byteorder='big')

def inteiro_para_string(numero):
    print("Número:", numero)
    if numero == 0:
        # Se 0 puder representar b'\x00' e não uma string vazia (pois string vazia daria erro na conversão para int)
        return '\x00' 
    tamanho = (numero.bit_length() + 7) // 8
    return numero.to_bytes(tamanho, byteorder='big').decode('utf-8', errors='replace')

@app_a.route('/')
def index():
    return render_template('index.html', servidor='A')

@app_a.route('/send_to_b', methods=['POST'])
def send_message_to_b():
    data = request.get_json()
    message = data.get('message')

    if message:
        print(f"Mensagem recebida para enviar a B: {message}")
        # Convertendo a mensagem para inteiro
        message_int = string_para_inteiro(message)

        print(f"Mensagem convertida para inteiro: {message_int}")
        encrypted_message = encript_message(message_int, Config.SERVER2_PUBLIC_EXPOENT, Config.SERVER2_PUBLIC_MODULE)

        messages_a_to_b.append(message)
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {'message': encrypted_message, 'sender': 'A'}
            response = requests.post(APP_B_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return jsonify({'status': 'Mensagem enviada para B com sucesso!'}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Erro ao enviar mensagem para B: {e}'}), 500
    return jsonify({'error': 'Mensagem não encontrada no corpo da requisição'}), 400

@app_a.route('/receive_from_b', methods=['POST'])
def receive_message_from_b():
    data = request.get_json()
    message = data.get('message')
    sender = data.get('sender')

    if message and sender == 'B':
        print(f"Mensagem recebida de B: {message}")
        decrypted_message_int = decript_message(Config.SERVER_PRIVATE_EXPOENT, Config.SERVER_MODULE, message)
        # Convertendo o número inteiro de volta para string
        decrypted_message = inteiro_para_string(decrypted_message_int)
        messages_received_from_b.append(decrypted_message)
        print(f"Servidor A recebeu de B: {decrypted_message}")
        return jsonify({'status': 'Mensagem recebida com sucesso!'}), 200
    return jsonify({'error': 'Mensagem inválida ou remetente incorreto'}), 400

@app_a.route('/messages_b', methods=['GET'])
def get_messages_from_b():
    return jsonify({'messages': messages_received_from_b}), 200

@app_a.route('/messages_sent_b', methods=['GET'])
def get_sent_messages_to_b():
    return jsonify({'messages': messages_a_to_b}), 200

if __name__ == '__main__':
    app_a.run(port=5000, debug=True)
