import random

def generate_response():
    # Choose a random length for the number: 1, 2, or 3 digits
    length = random.choice([1, 2, 3])
    # Generate a number where each digit is between 0 and 3
    response = int("".join(str(random.choice([0, 1, 2, 3])) for _ in range(length)))
    return response