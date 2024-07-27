from datetime import datetime


print(str(datetime.now()).split(".")[0])



def foo(i):
    if i != "statement":
        return "invalid"
    
    return "this is some important information"

def poo(i):
    if i == "statement":
        return "this is some important information"
    else:
        return "invalid"
