
import sys
sys.path.append("./predict/")
from Main import *

def run(jason):
    m = M()
    m.trainIt(2,10,10,2)
