import string
import itertools
import time

def brute_force_demo(target_password):
    charset = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    length = 5

    attempts = 0
    start_time = time.time()

    for guess_tuple in itertools.product(charset, repeat=length):
        guess = ''.join(guess_tuple)
        attempts += 1

        # Display current guess (optional, slows things down)
        print(f"\rTrying: {guess}", end="")

        if guess == target_password:
            end_time = time.time()
            print("\n\nPassword found!")
            print(f"Password: {guess}")
            print(f"Attempts: {attempts}")
            print(f"Time taken: {end_time - start_time:.4f} seconds")
            return

    print("\nPassword not found.")

if __name__ == "__main__":
    password = input("Enter a 5-letter lowercase password to test: ")

    if len(password) != 5 or not password.islower() or not password.isalpha():
        print("Password must be exactly 5 lowercase letters (a-z).")
    else:
        brute_force_demo(password)
