import json
import os.path

logpath = "logs"
paramfile = os.path.join(logpath, "hwparam.json")

def loadsetting(key):
    if os.path.exists(paramfile):
        paramsetting = json.loads(open(paramfile, "r").read())
        if key in paramsetting:
            return paramsetting[key]
    return None

def writesetting(key:str,value:str):
    try:
        paramsetting={}
        if not os.path.exists(logpath):
            os.mkdir(logpath)
        if os.path.exists(paramfile):
            paramsetting=json.loads(open(paramfile,"r").read())
        paramsetting[key]=value
        open(paramfile,"w").write(json.dumps(paramsetting))
        return True
    except:
        return False
