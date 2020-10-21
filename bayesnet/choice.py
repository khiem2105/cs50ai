import random

list = [1,2,3]
print(random.choices(list, weights = [0.1,0.7,0.2], k = 1))