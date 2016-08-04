import sys
sys.path.append("../../sketchfe/sketchfe")
sys.path.append('../predict/')
sys.path.append('../clusterer/')
sys.path.append('../classifiers/')
sys.path.append('../test/')
sys.path.append('../data/')
sys.path.append("../../libsvm-3.21/python")
from extractor import *
from FileIO import *
from newMethodPredictor import *
import os
import time
import numpy as np
import classesFile

from flask import Flask, request, render_template, flash, json
app = Flask(__name__)
predictor = None

files = classesFile.files

def newTraining(n,files, numclass, numfull,numpartial,k):
    extr = Extractor('../data/')
    fio = FileIO()

    for i in range(n/5):
        trainingName = '%s_%i__CFPK_%i_%i_%i_%i' % ('training',i, numclass, numfull, numpartial, k)
        trainingpath = '../data/newMethodTraining/' + trainingName
        features, isFull, classId, names, folderList = extr.loadfolders(  numclass   = numclass,
                                                                          numfull    = numfull,
                                                                          numpartial = numpartial,
                                                                          folderList = files[i*5:(i+1)*5])
        constarr = getConstraints(size=len(features), isFull=isFull, classId=classId)
        ckmeans = CKMeans(constarr, np.transpose(features), k)
        kmeansoutput = ckmeans.getCKMeans()

        # find heterogenous clusters and train svm
        trainer = Trainer(kmeansoutput, classId, features)
        heteClstrFeatureId, heteClstrId = trainer.getHeterogenous()
        trainer.trainSVM(heteClstrFeatureId, trainingpath)
        fio.saveTraining(names, classId, isFull, features, kmeansoutput,
                         trainingpath, trainingName)
        trainer.trainSVM(heteClstrFeatureId, trainingpath)

        nowCenter = np.zeros(len(features[0]))
        totalNumOfInstances = len(features)
        for cluster in kmeansoutput[0]:
            for instance in cluster:
                nowCenter += features[instance]
        nowCenter = nowCenter/totalNumOfInstances
        fio.saveOneFeature(trainingpath +'/' + str(i) + "__Training_Center_",nowCenter)





def PredictIt(n, q):
    extr = Extractor('../data/')
    fio = FileIO()
    numclass, numfull, numpartial = 10, 6, 3
    k = numclass
    l = []

    for i in range(n/5):
        pass


    for i in range(n/5):
        trainingName = '%s_%i__CFPK_%i_%i_%i_%i' % ('training',i, numclass, numfull, numpartial, k)
        trainingpath = '../data/newMethodTraining/' + trainingName
        names, classId, isFull, features, kmeansoutput, loadedFolders = fio.loadTraining(trainingpath + "/" + trainingName)
        predictor = newMethodPredictor(kmeansoutput, classId, trainingpath)
        predictor.setFiles(files[i*5:(i+1)*5])

        a = predictor.predictByString(q)
        b = fio.loadOneFeature(trainingpath +'/' + str(i) + "__Training_Center_")




@app.route("/", methods=['POST','GET'])
def handle_data():
    global predictor
    timeStart = time.time()
    try:
        queryjson = request.args.get('json')
        classProb = PredictIt(10,queryjson)
        print 'Server responded in %.3f seconds' % float(time.time()-timeStart)
        return getBestPredictions(classProb, 5)
    except Exception as e:
        flash(e)
        print(request.values)
        return "Error" + str(e)

@app.route("/send", methods=['POST','GET'])
def return_probabilities():
    print 'SERVER: return_probabilities method called'
    raise NotImplementedError

@app.route("/home", methods=['GET'])
def homepage():
    print 'SERVER: homepage method called'
    return render_template("index.html")

def main():
    ForceTrain = True
    numclass, numfull, numpartial = 10, 6, 3
    k = numclass

    n = 10

    # if training data is already computed, import
    if  not ForceTrain:
        pass
        # names, classId, isFull, features, kmeansoutput = fio.loadTraining(trainingpath + "/" + trainingName)
    else:
        newTraining(n , files, numclass, numfull, numpartial, k)


    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', debug=False)
    print 'Server ended'
if __name__ == '__main__':main()
