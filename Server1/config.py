import os

class Config:
    # Chaves próprias do Servidor A (e1, d1, n1)
    SERVER_PRIVATE_EXPOENT = int(os.getenv('SERVER_A_PRIVATE_EXPOENT', '2753'))
    SERVER_MODULE = int(os.getenv('SERVER_A_MODULE', '3233'))
    SERVER_PUBLIC_EXPOENT = int(os.getenv('SERVER_A_PUBLIC_EXPOENT', '17'))
    
    # Chave pública do Servidor B (e2, n2) - ATUALIZADA
    SERVER2_PUBLIC_EXPOENT = int(os.getenv('SERVER_B_PUBLIC_EXPOENT', '17'))
    SERVER2_PUBLIC_MODULE = int(os.getenv('SERVER_B_PUBLIC_MODULE', '3127')) # Novo n2