import random
import utils as ut
from sympy import isprime

def generate_prime():
    while True:
        prime = random.randint(10**50, 10**51)
        if isprime(prime):
            return prime 
        
def choose_e(phi, n):
    while True:
        e = random.randint(2, phi-1) # has to be less than phi and greater than 1
        if isprime(e) and ut.gdc(e, phi) == 1 and ut.gdc(e, n) == 1: 
            return e

def calculate_d(e, phi):
    return pow(e, -1, phi)
    
def generate_keys():
    # generate two distinct prime numbers
    # recive the prime numbers
    p = generate_prime()
    q = generate_prime()
    # check if p and q are equal, if true assign q a new prime number
    if p == q:
        q = generate_prime()

    # calculate n
    n = p * q
    
    # calculate phi(totiente) using the Euler function
    phi = (p-1)*(q-1)

    # choose e
    e = choose_e(phi, n)

    # calculate d
    d = calculate_d(e, phi)

    return e, d, n

def encript_message(message, e, n):    
    message_crip = pow(message, e, n)

    return message_crip

def decript_message(PD, PN, signature):
    
    decrypted_signature = pow(signature, PD, PN)

    return decrypted_signature
