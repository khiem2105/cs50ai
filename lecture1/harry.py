from logic import *

rain = Symbol("rain") #It is raining
hagrid = Symbol("hagrid") #Harry visit Hagrid
dumbledore = Symbol("dumbledore") #Harry visit Dumbledore

knowledge = And(
    Implication(Not(rain), hagrid),
    Or(hagrid,dumbledore),
    Not(And(hagrid, dumbledore)),
    dumbledore
)    

print(model_check(knowledge, rain))