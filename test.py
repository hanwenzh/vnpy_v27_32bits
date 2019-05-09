
import functools

import ctypes
from ctypes import *

def log(fun):
    def wrapper(*args, **kwargs):
        print "call %s" %fun.__name__
        return fun(*args, **kwargs)
    return wrapper

@log
def now():
    print "nooooooow"


print now.__name__

now()

int3 = functools.partial(int, base=3)

print(int3('21'))



a = (x for x in range(10))
for i in a:
    print i

a = [x for x in range(10)]
for i in a:
    print i

b1 = c_char_p()
b1.value = "0"*20
print("11111")
