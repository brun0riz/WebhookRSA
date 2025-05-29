######################### GCD #########################
# Euclid's algorithm to find the GCD of two numbers
def gdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a