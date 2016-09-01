import pickle
from draw import *

"""
Loads test results - with pickle - and generates plots, without a
undergoing a testing process again.

Do that if you want different plots than templates, or in order
to regenerate the plots with different parameters.
"""

numclass, numfull, numpartial = 10, 80, 80
K = [250]  # :O
# K = [numclass]
N = range(1, numclass)
import numpy as np

C = np.linspace(0, 100, 51, endpoint=True)
C = [int(c) for c in C]

#folderName = '%s___%i_%i' % ('nicicionWithCuda_fulldata', 10, 20)
folderName = 'complexCudaCKMeanTest___250_70_80_250'
trainingpath = '../data/training/' + folderName

accuracy = pickle.load(open(trainingpath + '/' "accuracy.p", "r"))
reject_rate = pickle.load(open(trainingpath + '/' "reject.p", "r"))

draw_n_Acc(accuracy, c=0, k=K[0], isfull=True, reject_rate=reject_rate, path=trainingpath)
draw_n_Acc(accuracy, c=0, k=K[0], isfull=False, reject_rate=reject_rate, path=trainingpath)

#draw_N_C_Acc(accuracy, N, C, k=K[0], isfull=True, path=trainingpath)
#draw_N_C_Reject_Contour(reject_rate, N, C, k=K[0], isfull=True, path=trainingpath)
#draw_N_C_Acc_Contour(accuracy, N, C, k=K[0], isfull=True, path=trainingpath)  # Surface over n and c
#draw_N_C_Reject_Contour(reject_rate, N, C, k=K[0], isfull=True, path=trainingpath)
#draw_K_Delay_Acc(accuracy, reject_rate, K=K, C=C, n=1, isfull=True, path=trainingpath)
#draw_Reject_Acc([accuracy], [reject_rate], N=[1, 2], k=K[0], isfull=True, labels=['Ck-means'], path=trainingpath)

#draw_N_C_Acc(accuracy, N, C, k=K[0], isfull=False, path=trainingpath)
#draw_N_C_Reject_Contour(reject_rate, N, C, k=K[0], isfull=False, path=trainingpath)
#draw_N_C_Acc_Contour(accuracy, N, C, k=K[0], isfull=False, path=trainingpath)  # Surface over n and c
#draw_N_C_Reject_Contour(reject_rate, N, C, k=K[0], isfull=False, path=trainingpath)
#draw_K_Delay_Acc(accuracy, reject_rate, K=K, C=C, n=1, isfull=False, path=trainingpath)
#draw_Reject_Acc([accuracy], [reject_rate], N=[1, 2], k=K[0], isfull=False, labels=['Ck-means'], path=trainingpath)
print 'End'
