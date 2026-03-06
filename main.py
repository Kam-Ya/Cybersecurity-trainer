from cracker import *
import string
from userinput import *
from player import *


testPolicy = PasswordPolicy
testPolicy.allowed_chars = string.ascii_lowercase
testPolicy.allowed_chars = testPolicy.allowed_chars + string.ascii_uppercase
testPolicy.max_len = 5

test = prompt_password(testPolicy)

print(test)

brute_force_demo(test.password)
