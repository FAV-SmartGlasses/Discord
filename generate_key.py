import random

KEY_LENGTH = 32

CHARACTERS = list("qwertyuiopasdfghjklzxcvbnm-1234567890-QWERTYUIOPASDFGHJKLZXCVBNM")

def generate_key(key_length):
    key = ""
    for i in range(key_length):
        key += random.choice(CHARACTERS)

    return key

if __name__ == "__main__":
    print(generate_key(KEY_LENGTH))