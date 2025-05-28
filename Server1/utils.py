######################### PRINTS CHUNKS #########################
def print_em_blocos(texto):
    for i in range(0, len(texto), 8):
        print(texto[i:i+8], end="  ")
        if (i // 8 + 1) % 4 == 0:
            print()

def print_blocos(array):
    for bloco in enumerate(array, start=0):
        print(bloco)

######################### SHA ROTATION #########################
def right_rotate(value, rotate_bits):
    # Converte o valor para inteiro se necessário e realiza a rotação à direita
    value = int(value, 2)
    return (value >> rotate_bits | value << (32 - rotate_bits)) & 0xFFFFFFFF

######################### FRAC PART #########################
def get_fractional_part(number):
    fractional_part = number - int(number)
    return fractional_part 

######################### GET PRIMES #########################
def get_prime_numbers(quant_prime):
    prime_numbers = []
    i = 2

    while len(prime_numbers) != quant_prime:
        # test to see if i is prime
        # if i is divisible by any number other than 1 and itself, it is not prime
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                break
        else:
            prime_numbers.append(i)
        i += 1

    return prime_numbers

######################### GCD #########################
# Euclid's algorithm to find the GCD of two numbers
def gdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a

######################### CONVERTIONS #########################
def string_to_int(frase):
    resultado = ''
    for char in frase:
        ascii_val = ord(char)
        resultado += f'{ascii_val:03}'  # força 3 dígitos por caractere
    return int(resultado)

def int_to_string(numero):
    s = str(numero)
    if len(s) % 3 != 0:
        raise ValueError("Número inválido: deve conter múltiplos de 3 dígitos")
    
    frase = ''
    for i in range(0, len(s), 3):
        ascii_val = int(s[i:i+3])
        frase += chr(ascii_val)
    return frase

def verify_authenticity(hash_original, hash_altered):
    print(f"Hash original: {hash_original}")
    print(f"Hash altered: {hash_altered}")

    if hash_original == hash_altered:
        print("The files are identical.")
    else:
        print("The file has been modified.")

def openfile(file_path):
    try:
        if file_path.endswith('.txt'):
            print("Opening file as text")
            with open(file_path, 'r', encoding='utf-8') as file:
                im =  file.read()
        else:
            with open(file_path, 'rb') as file:
                im =  file.read()
    except Exception as e:
        print("Error opening file:", e)
        return None
    
    return im