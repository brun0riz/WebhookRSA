import os

class Config:
    # Chaves próprias do Servidor B (e2, d2, n2) - ATUALIZADAS
    SERVER_PRIVATE_EXPOENT = int(os.getenv('SERVER_B_PRIVATE_EXPOENT', '2661')) # Novo d2
    SERVER_MODULE = int(os.getenv('SERVER_B_MODULE', '3127')) # Novo n2
    SERVER_PUBLIC_EXPOENT = int(os.getenv('SERVER_B_PUBLIC_EXPOENT', '17'))
    
    # Chave pública do Servidor A (e1, n1)
    SERVER1_PUBLIC_EXPOENT = int(os.getenv('SERVER_A_PUBLIC_EXPOENT', '17'))
    SERVER1_PUBLIC_MODULE = int(os.getenv('SERVER_A_MODULE', '3233'))