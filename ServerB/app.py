# ServerB/app.py
from flask import Flask, json, request, jsonify, render_template
from RSA.rsa import generate_keys, encript_message, decript_message
from config import AppConfig
import requests
import time
import threading
import logging
from dotenv import load_dotenv # Para carregar o .env explicitamente

load_dotenv() # Carrega ServerB/.env

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ServerB")

app_b = Flask(__name__)
current_config = AppConfig(server_id='B')

keys_fully_exchanged = threading.Event()

messages_b_to_a = [] # Mensagens que B enviou para A
messages_received_from_a = [] # Mensagens que B recebeu de A

def string_para_inteiro(texto):
    logger.debug(f"Texto para converter: '{texto}'")
    encoded_text = texto.encode('utf-8')
    return int.from_bytes(encoded_text, byteorder='big')

def inteiro_para_string(numero):
    logger.debug(f"Número para converter: {numero}")
    if numero == 0 and current_config.SERVER_MODULE is not None and current_config.SERVER_MODULE > 0 :
        return "" 
    try:
        num_bits = numero.bit_length()
        num_bytes = (num_bits + 7) // 8
        byte_representation = numero.to_bytes(num_bytes, byteorder='big')
        return byte_representation.decode('utf-8', errors='replace')
    except Exception as e:
        logger.error(f"Erro ao converter inteiro {numero} para string: {e}")
        return f"[Erro na decodificação: {numero}]"

@app_b.route('/')
def index():
    return render_template('index.html', servidor=current_config.SERVER_ID)

@app_b.route('/exchange_key', methods=['POST'])
def handle_exchange_key():
    data = request.get_json()
    try:
        e_other = int(data['e'])
        n_other = int(data['n'])
        sender_id = data.get('sender_id')

        if sender_id == current_config.OTHER_SERVER_ID: # Espera 'A'
            current_config.update_other_server_keys(e_other, n_other)
            logger.info(f"Recebeu chave pública do Servidor {sender_id}.")
            if current_config.are_all_keys_set():
                keys_fully_exchanged.set()
                logger.info("Troca de chaves completa!")
            return jsonify({'status': f'Servidor {current_config.SERVER_ID} recebeu a chave de {sender_id}'}), 200
        else:
            logger.warning(f"Recebimento de chave de remetente inválido: {sender_id}")
            return jsonify({'error': 'Remetente inválido'}), 400
    except Exception as e:
        logger.error(f"Erro ao processar /exchange_key: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def attempt_send_own_key():
    if not current_config.SERVER_PUBLIC_EXPOENT:
        logger.error("Chaves próprias não geradas. Não é possível enviar.")
        return False
    payload = {
        'e': current_config.SERVER_PUBLIC_EXPOENT,
        'n': current_config.SERVER_MODULE,
        'sender_id': current_config.SERVER_ID
    }
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info(f"Tentando enviar chave para {current_config.OTHER_SERVER_URL_RECEIVE_KEY}")
        response = requests.post(current_config.OTHER_SERVER_URL_RECEIVE_KEY, headers=headers, data=json.dumps(payload), timeout=5)
        response.raise_for_status()
        logger.info(f"Chave pública enviada com sucesso para o outro servidor: {response.json().get('status')}")
        return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha ao enviar chave pública: {e}")
        return False

def key_exchange_startup_logic():
    logger.info(f"Servidor {current_config.SERVER_ID}: Iniciando lógica de troca de chaves...")
    d_own, e_own, n_own = generate_keys()
    current_config.update_own_keys(d_own, e_own, n_own)

    max_retries = 12
    retry_delay = 5
    for attempt in range(max_retries):
        if keys_fully_exchanged.is_set():
            logger.info("Chaves já trocadas e confirmadas.")
            break
        logger.info(f"Tentativa de troca de chaves ({attempt + 1}/{max_retries})...")
        sent_successfully = attempt_send_own_key()
        if current_config.are_all_keys_set():
            keys_fully_exchanged.set()
            logger.info("Todas as chaves configuradas, troca considerada completa.")
            break
        if attempt < max_retries - 1:
            logger.info(f"Aguardando {retry_delay}s para próxima tentativa de troca de chaves.")
            time.sleep(retry_delay)
        else:
            logger.error("Máximo de tentativas de troca de chaves atingido. Verifique o outro servidor.")

@app_b.route('/send_to_a', methods=['POST']) # Endpoint para B enviar para A
def send_message_to_other_server():
    if not keys_fully_exchanged.is_set():
        logger.warning("Tentativa de enviar mensagem antes da troca de chaves estar completa.")
        return jsonify({'error': 'Troca de chaves pendente. Tente novamente mais tarde.'}), 503
    data = request.get_json()
    message_text = data.get('message')
    if not message_text:
        logger.info("Recebida tentativa de enviar mensagem vazia.")
        # message_text = ""

    logger.info(f"Mensagem STRING recebida para enviar a A: '{message_text}'")
    message_int = string_para_inteiro(message_text)
    logger.info(f"Mensagem convertida para INTEIRO: {message_int}")
    
    try:
        encrypted_message = encript_message(message_int, current_config.OTHER_SERVER_PUBLIC_EXPOENT, current_config.OTHER_SERVER_PUBLIC_MODULE)
    except ValueError as e:
        logger.error(f"Erro de valor durante a criptografia: {e} (Mensagem int: {message_int}, Módulo: {current_config.OTHER_SERVER_PUBLIC_MODULE})")
        return jsonify({'error': f'Erro ao criptografar mensagem: {e}'}), 500

    logger.info(f"Mensagem CRIPTOGRAFADA (enviada para A): {encrypted_message}")
    timestamp = time.time()
    messages_b_to_a.append({'text': message_text, 'timestamp': timestamp})
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'message': encrypted_message, 'sender_id': current_config.SERVER_ID}
        response = requests.post(current_config.OTHER_SERVER_URL_RECEIVE_MESSAGE, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return jsonify({'status': 'Mensagem enviada para A com sucesso!'}), 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar mensagem para A: {e}", exc_info=True)
        return jsonify({'error': f'Erro ao enviar mensagem para A: {e}'}), 500

@app_b.route('/receive_message', methods=['POST'])
def receive_message_from_other_server():
    if not current_config.SERVER_PRIVATE_EXPOENT:
        logger.warning("Tentativa de receber mensagem antes das chaves próprias estarem prontas.")
        return jsonify({'error': 'Servidor não pronto para receber mensagens criptografadas.'}), 503
    data = request.get_json()
    encrypted_message = data.get('message')
    sender_id = data.get('sender_id')
    if encrypted_message is not None and sender_id == current_config.OTHER_SERVER_ID: # Espera 'A'
        logger.info(f"Mensagem CRIPTOGRAFADA recebida de {sender_id}: {encrypted_message}")
        decrypted_message_int = decript_message(current_config.SERVER_PRIVATE_EXPOENT, current_config.SERVER_MODULE, encrypted_message)
        logger.info(f"Mensagem DESCRIPTOGRAFADA (inteiro): {decrypted_message_int}")
        decrypted_message_text = inteiro_para_string(decrypted_message_int)
        logger.info(f"Mensagem DESCRIPTOGRAFADA (string): '{decrypted_message_text}'")
        timestamp = time.time()
        messages_received_from_a.append({'text': decrypted_message_text, 'timestamp': timestamp})
        return jsonify({'status': 'Mensagem recebida com sucesso!'}), 200
    return jsonify({'error': 'Mensagem inválida ou remetente incorreto'}), 400

@app_b.route('/messages_a', methods=['GET']) # Cliente B pede mensagens recebidas de A
def get_messages_from_a():
    return jsonify({'messages': messages_received_from_a}), 200

@app_b.route('/messages_sent_a', methods=['GET']) # Cliente B pede mensagens que B enviou para A
def get_sent_messages_to_a():
    return jsonify({'messages': messages_b_to_a}), 200

@app_b.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "server_id": current_config.SERVER_ID,
        "keys_fully_exchanged": keys_fully_exchanged.is_set(),
        "all_config_keys_set": current_config.are_all_keys_set(),
        "own_public_exponent_set": current_config.SERVER_PUBLIC_EXPOENT is not None,
        "own_module_set": current_config.SERVER_MODULE is not None,
        "other_server_public_exponent_set": current_config.OTHER_SERVER_PUBLIC_EXPOENT is not None,
        "other_server_module_set": current_config.OTHER_SERVER_PUBLIC_MODULE is not None,
    })

if __name__ == '__main__':
    key_exchange_thread = threading.Thread(target=key_exchange_startup_logic, daemon=True)
    key_exchange_thread.start()
    logger.info(f"Servidor B iniciando na porta {current_config.OWN_PORT}. Aguardando troca de chaves...")
    app_b.run(host='0.0.0.0', port=current_config.OWN_PORT, debug=True, use_reloader=False)