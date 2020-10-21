from nim import *

ai = train(10000)
actions = ai.available_actions([1,3,5,7])
print(len(actions))
play(ai)
