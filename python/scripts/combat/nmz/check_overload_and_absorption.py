from modules.core.plugin_client import varbit

def absorption():
    absorption = varbit(3956)
    print(f"Absorption: {absorption}")
    if absorption < 100:
        print(f"drinking absorption: {absorption}")
        return False
    return True
    
def overload():
    overload = varbit(3955)
    print(f"ovl: {overload}")
    if overload <= 0:
        print(f"drinking ovl: {overload}")
        return False
    return True
    
