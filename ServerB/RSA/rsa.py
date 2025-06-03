def encript_message(message, e, n):    
    message_crip = pow(message, e, n)

    return message_crip

def decript_message(PD, PN, signature):
    
    decrypted_signature = pow(signature, PD, PN)

    return decrypted_signature
