import os

class AppConfig:
    def __init__(self, server_id):
        self.SERVER_ID = server_id

        # Chaves próprias do servidor (serão geradas no início)
        self.SERVER_PUBLIC_EXPOENT = None
        self.SERVER_PRIVATE_EXPOENT = None
        self.SERVER_MODULE = None

        # Chaves públicas do OUTRO servidor (serão recebidas)
        self.OTHER_SERVER_PUBLIC_EXPOENT = None
        self.OTHER_SERVER_PUBLIC_MODULE = None

        # Configurações de rede baseadas no server_id
        if self.SERVER_ID == 'A':
            self.OWN_PORT = int(os.getenv('SERVER_A_PORT', 5000))
            self.OTHER_SERVER_HOST = os.getenv('SERVER_B_HOST', '127.0.0.1')
            self.OTHER_SERVER_PORT = int(os.getenv('SERVER_B_PORT', 5001))
            self.OTHER_SERVER_ID = 'B'
        elif self.SERVER_ID == 'B':
            self.OWN_PORT = int(os.getenv('SERVER_B_PORT', 5001))
            self.OTHER_SERVER_HOST = os.getenv('SERVER_A_HOST', '127.0.0.1')
            self.OTHER_SERVER_PORT = int(os.getenv('SERVER_A_PORT', 5000))
            self.OTHER_SERVER_ID = 'A'
        else:
            raise ValueError("server_id deve ser 'A' ou 'B'")

        # URLs para comunicação
        self.OTHER_SERVER_URL_RECEIVE_KEY = f"http://{self.OTHER_SERVER_HOST}:{self.OTHER_SERVER_PORT}/exchange_key"
        self.OTHER_SERVER_URL_RECEIVE_MESSAGE = f"http://{self.OTHER_SERVER_HOST}:{self.OTHER_SERVER_PORT}/receive_message"
        
        print(f"Config para Servidor {self.SERVER_ID}: Próprio Porto={self.OWN_PORT}, Outro Servidor={self.OTHER_SERVER_HOST}:{self.OTHER_SERVER_PORT}")

    def update_own_keys(self, private_exponent, public_exponent, module):
        self.SERVER_PRIVATE_EXPOENT = private_exponent
        self.SERVER_PUBLIC_EXPOENT = public_exponent
        self.SERVER_MODULE = module
        print(f"Servidor {self.SERVER_ID}: Chaves próprias atualizadas.")

    def update_other_server_keys(self, public_exponent, module):
        self.OTHER_SERVER_PUBLIC_EXPOENT = public_exponent
        self.OTHER_SERVER_PUBLIC_MODULE = module
        print(f"Servidor {self.SERVER_ID}: Chaves do servidor {self.OTHER_SERVER_ID} atualizadas.")

    def are_all_keys_set(self):
        return all([
            self.SERVER_PUBLIC_EXPOENT is not None,
            self.SERVER_PRIVATE_EXPOENT is not None,
            self.SERVER_MODULE is not None,
            self.OTHER_SERVER_PUBLIC_EXPOENT is not None,
            self.OTHER_SERVER_PUBLIC_MODULE is not None
        ])