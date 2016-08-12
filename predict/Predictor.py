"""
Predictor
Ahmet BAGLAN
14.07.2016
"""
import sys
sys.path.append('../classifiers')
sys.path.append("../../libsvm-3.21/python/")
sys.path.append('../data/')
import math
import numpy as np

from trainer import *
from shapecreator import *
from FeatureExtractor import *
from scipy.spatial import distance

class Predictor:
    """The predictor class implementing functions to return probabilities"""
    def __init__(self, kmeansoutput, classId, subDirectory, svm = None):
        self.kmeansoutput = kmeansoutput
        self.classId = classId
        self.subDirectory = subDirectory
        self.svm = svm

    def getDistance(self, x, y):
        """Computes euclidian distance between x instance and y instance
        inputs: x,y instances
        kmeansoutput: distance"""
        return distance.euclidean(x, y)
    
    def clusterProb(self, instance, priorProb):
        """
        Returns P(Ck|x)
        normalProb : probability that was calculated in trainer
        instance: feature list of the instance to be queried"""

        centers = self.kmeansoutput[1]
        dist = [self.getDistance(instance, centers[idx]) for idx in range(len(centers))]
        diste_ = [math.exp(-1*abs(d)) for d in dist]
        clustProb = [diste_[idx]*priorProb[idx] for idx in range(len(centers))]

        #import numpy as np
        #import matplotlib.pyplot as plt

        #fig = plt.figure()
        #plt.scatter(range(len(diste_)), diste_, alpha=0.5)
        #plt.show()

        return clustProb

    def svmProb(self, model, instance):
        """Predicts the probability of the given model"""

        ####Prevent Printing----------------------------------------
        import sys
        class NullWriter(object):
            def write(self, arg):
                pass
        nullwrite = NullWriter()
        oldstdout = sys.stdout
        sys.stdout = nullwrite # disable kmeansoutput

        y = [0]
        p_label, p_acc, p_val = svm_predict(y, instance, model, '-b 1')

        sys.stdout = oldstdout
        ### Prevent printing ended-----------------------------------

        return (p_label, p_val)


    def predictByInstance(self, instance):
        # find the probability of given feature to belong any of athe classes
        priorClusterProb = self.calculatePriorProb()
        classProb = self.calculatePosteriorProb(instance, priorClusterProb)
        return classProb

    def predictByPath(self, fullsketchpath):
        instance = featureExtract(fullsketchpath)
        priorClusterProb = self.calculatePriorProb()
        classProb = self.calculatePosteriorProb(instance, priorClusterProb)
        return classProb

    def predictByString(self, jstring):
        loadedSketch = shapecreator.buildSketch('json', jstring)
        featextractor = IDMFeatureExtractor()
        instance = featextractor.extract(loadedSketch)
        priorClusterProb = self.calculatePriorProb()
        classProb = self.calculatePosteriorProb(instance, priorClusterProb)
        return classProb

    def calculatePosteriorProb(self, instance, priorClusterProb):
        """
        #features : feature array
        #kmeansoutput : list [ List of Cluster nparray, List of Cluster Center nparray]
        #p  robability : P(Ck)
        # Returns P(Si|x)
        """

        # dict of probabilities of given instance belonging to every possible class
        # initially zero
        outDict = dict.fromkeys([i for i in set(self.classId)], 0.0)
        
        homoClstrFeatureId, homoClstrId = self.getHomogenous()
        heteClstrFeatureId, heteClstrId = self.getHeterogenous()

        clusterProb = self.clusterProb(instance, priorClusterProb)#Probability list to be in a cluster

        # normalize cluster probability to add up to 1
        clustersum = sum(clusterProb)
        clusterProb = [x/clustersum for x in clusterProb]

        clusterFeatureId = self.kmeansoutput[0]

        for clstrid in range(len(clusterFeatureId)):
            probabilityToBeInThatCluster = clusterProb[clstrid]
            if clstrid in homoClstrId:
                
                # if homogeneous cluster is empty, then do not
                # process it and continue
                if len(clusterFeatureId[clstrid]) == 0:
                    continue
                
                # if homogeneous then only a single class which is the first
                # feature points class
                classesInCluster = [self.classId[int(clusterFeatureId[clstrid][0])]]
                
            elif clstrid in heteClstrId:
                if not self.svm:
                    modelName = self.subDirectory + "/clus" + str(heteClstrId.index(clstrid)) + ".model"
                    m = svm_load_model(modelName)
                    classesInCluster = m.get_labels()
                    labels, svmprobs = self.svmProb(m, [instance.tolist()])
                else:
                    labels, _, svmprobs = self.svm.predict(int(heteClstrId.index(clstrid)), [instance.tolist()])
                    classesInCluster = self.svm.getlabels(heteClstrId.index(clstrid))
                
            for c in range(len(classesInCluster)):
                probabilityToBeInThatClass = 1 if clstrid in homoClstrId else svmprobs[0][c]
                outDict[int(classesInCluster[c])] += probabilityToBeInThatCluster * probabilityToBeInThatClass

        return outDict

    def calculatePriorProb(self):
        """
        Returns prior probabilities list of being in a cluster
        p = len(cluster)/len(total)
        """
        clusterFeatureId = self.kmeansoutput[0]
        numFeatures = sum([len(cluster) for cluster in clusterFeatureId])

        prob = [len(clusterFeatureId[index]) / float(numFeatures) for index in range(len(clusterFeatureId))]

        return prob

    def getHeterogenous(self):
        """
        Gets clusters which are heterogenous
        kmeansoutput :(heterogenousClusters,heterogenousClusterId) -> heterogenous clusters, id's of heterougenous clusters
        """
        heterogenousClusters = list()
        heterogenousClusterId = list()
        for clusterId in range(len(self.kmeansoutput[0])):
            # if class id of any that in cluster of clusterId is any different than the first one
            if any(x for x in range(len(self.kmeansoutput[0][clusterId])) if
                   self.classId[int(self.kmeansoutput[0][clusterId][0])] != self.classId[int(self.kmeansoutput[0][clusterId][x])]):
                heterogenousClusters.append(self.kmeansoutput[0][clusterId])
                heterogenousClusterId.append(clusterId)
        return heterogenousClusters, heterogenousClusterId

    def getHomogenous(self):
        """
        Gets clusters which are homogenous
        kmeansoutput: (homoCluster,homoIdClus) -> homogenous clusters, id's of homogenous clusters
        """
        homoCluster = list()
        homoIdClus = list()
        for clusterId in range(len(self.kmeansoutput[0])):
            # if class id of any that in cluster of clusterId is any different than the first one
            if not any(x for x in range(len(self.kmeansoutput[0][clusterId])) if
                       self.classId[int(self.kmeansoutput[0][clusterId][0])] != self.classId[int(self.kmeansoutput[0][clusterId][x])]):
                homoCluster.append(self.kmeansoutput[0][clusterId])
                homoIdClus.append(clusterId)
        return homoCluster, homoIdClus

    def getBestPredictions(self,classProb, n):
        a = sorted(classProb, key=classProb.get, reverse=True)[:n]
        l = ''
        l1 = ''
        for i in a:
            l1 += str(classProb[i])
            l += str(i)
            l += '&'
            l1 += '&'
        l1 = l1[:-1]
        return l + l1

    def ServerOutput(self, queryjson, n):
        classPr = self.predictByString(str(queryjson))
        return self.getBestPredictions(classPr, n)

    def getSV(self):
        return self.svm.getSV()


