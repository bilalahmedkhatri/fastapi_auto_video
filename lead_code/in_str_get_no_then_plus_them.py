import random
import string

char = string.ascii_letters + string.digits + "*+-/"

ren = ''.join(random.choices(char, k=50))

print(ren)

# find int in this string.
integer = ''.join(filter(str.isdigit, ren))
pun = ''.join(filter(lambda x: x in string.punctuation, ren))


print(integer, pun)

# number = []
# punctuation = []
# # now plus them.
# for w in integer:
#     print(w)
#     if w in string.punctuation:
#         print(f"Found punctuation: {w}")
#         punctuation.append(w)
#     elif w in string.digits:
#         number.append(w)

result = 0    
for n in integer:
    for p in pun:
        print(f"Adding {n} for punctuation {p}")
        # result = result p (n) 
        
        
        
# print(f"punctuation: {punctuation}")
# print(f"Result: {result}")
        
        
# plus_int = sum(int(digit) for digit in integer, if string.pun)

# print(plus_int)