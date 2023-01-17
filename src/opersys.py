from platform import uname


# temporary fix for wrong detection in win 11
def get_release():
    pf = uname()
    ver = pf.version
    if int(ver[5:]) > 22000 and pf.system.lower() == "windows":
        return "11"
    return ver
