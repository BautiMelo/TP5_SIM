import random

valA0 = [1000,1500,2000]

def integ(h):

    t0 = 0
#    A0 = random.choice(valA0)
    A0 = 2000
    
    A = A0
    t1 = t0
    steps = [t1,A]

    while A > 0:
        A = A + ((-68- (A**2 / A0)  )* h)
        t1 = t1 + h
        steps.append([t1,A])
        

    return [t1, steps]

time,steps = integ(0.1)
print(time)
for i in steps:
    print(i)