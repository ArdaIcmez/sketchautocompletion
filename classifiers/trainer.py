"""
Classifier trainer
Ahmet BAGLAN - Arda ICMEZ 
14.07.2016
"""
from svmutil import *
from numpy.random import rand
import numpy as np
import matplotlib.pyplot as plt
from ckmeans import *
from getConstraints import *

def trainSVM(featArr, clusArr, labArr) :

    #label = labArr.tolist()
    label = labArr
    order = 0
    for i in clusArr:
        #Find corresponding labels, create 'y' list
        y = []
        x = []
        
        for j in i:
            j = int(j)
            y.append(label[j])
            x.append(featArr[j].tolist())

        print y, x
        prob  = svm_problem(y, x)
        param = svm_parameter('-t 2 -c 4')  # Gamma missing
        
        m = svm_train(prob, param)
        svm_save_model('clus' + `order` + '.model', m)
        order+=1

def computeProb(numIns, clusArr):
    prob = []
    for c in clusArr:
        prob.append(float(len(c))/numIns)
    return prob

def main():
########## Test Case  #######################

    

    NUMPOINTS = 200;
    NUMCLASS = 12;
    POINTSPERCLASS = NUMPOINTS/NUMCLASS

    xmin = 0;
    xmax = 100;
    ymin = 0;
    ymax = 100;

    features = np.array([np.zeros(NUMPOINTS), np.zeros(NUMPOINTS)])
    centers = np.array([np.zeros(NUMCLASS), np.zeros(NUMCLASS)])
    isFull = [np.random.randint(0, 2) for r in xrange(NUMPOINTS)]

    classId = list()
    index = 0
##################################### PREPARE FEATURES ###################################
    for i in range(0, NUMCLASS): 
        classId.extend([i]*POINTSPERCLASS)
        centerx = int(np.random.random()*xmax - xmin)
        centery = int(np.random.random()*ymax - ymin)
        centers[0][i] = centerx
        centers[1][i] = centery

        for j in range(0, POINTSPERCLASS):
            datax = int(np.random.normal(loc = centerx, scale = 3))
            datay = int(np.random.normal(loc = centery, scale = 3))

            features[0][index] = datax
            features[1][index] = datay
            index += 1

    # add the remaning points, from integer division
    remainingPoints = NUMPOINTS - POINTSPERCLASS*NUMCLASS
    if (remainingPoints):
        # select the center randomly
        randc = np.random.randint(0, max(classId))
        classId.extend([randc]*remainingPoints)
        for i in range (NUMPOINTS - POINTSPERCLASS*NUMCLASS):
            datax = int(np.random.normal(loc = centers[0][randc], scale = 3))
            datay = int(np.random.normal(loc = centers[1][randc], scale = 3))
            features[0][index] = datax
            features[1][index] = datay
            index += 1
#######################################################################################

    test = getConstraints(NUMPOINTS, isFull, classId)
    
    k = 13
    kmeans = CKMeans(test,features,k)
    output = kmeans.getCKMeans()
    
    """
    probabilities = computeProb(len(labels),clusters)

    print probabilities
    """
#################################################

    trainSVM(np.transpose(features), output[0], classId)
   

    
if __name__ == '__main__':
    main()
    #profile.run('print main(); print')



