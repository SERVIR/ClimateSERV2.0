'''
Created on Jan 30, 2015
@author: jeburks

Modified starting from Sept 2015
@author: Kris Stanton
'''

import os
import sys
#sys.path.insert(0, os.getcwd())
#print("ZMQCHIRPSDataWorker: sys.path: " + str(sys.path))

import json
import zmq
import time
import random


# Deprecating Legacy
#import CHIRPS.utils.locallog.locallogging as llog
#import CHIRPS.utils.configuration.parameters as params


# Data Calculator
# import CHIRPS.utils.file.DataCalculator as dc
#import api_v2.processing_objects.zmq.legacy.supporting_files.utils.file.DataCalculator as dc
import legacy.supporting_files.utils.file.DataCalculator as dc


# Mask Temp Storage
#import CHIRPS.utils.file.MaskTempStorage  as mst
#import api_v2.processing_objects.zmq.legacy.supporting_files.utils.file.MaskTempStorage  as mst
import legacy.supporting_files.utils.file.MaskTempStorage  as mst


# Math Operations
#import CHIRPS.utils.processtools.pMathOperations as pMath
#import api_v2.processing_objects.zmq.legacy.supporting_files.utils.processtools.pMathOperations as pMath
import legacy.supporting_files.utils.processtools.pMathOperations as pMath





class ZMQCHIRPSDataWorker():
    #logger = llog.getNamedLogger("request_processor")
    inputreceiver=None
    outputreceiver = None
    operatingData = None
    inputconn = None
    outputConn = None
    name = None
    
    # KS Refactor 2015 // Turns out the worker duplication issue was really just a double logging issue combined with an old ghost instance.
    # logging and outputing the PID to be sure this is not a duplication issue.
    pid = None
    
    def __getUniqueWorkerNameString__(self):
        return self.name + ":("+self.pid+")"
    
    def __doWork__(self):
        try:
            bounds, clippedmask = self.__readMask__(self.operatingData['uid'])
            #self.logger.debug("Worker: " +str(self.name)+ " : Value of bounds: " + str(bounds))  # ks refactor
            self.operatingData['clippedmask'] = clippedmask
            if (self.operatingData['intervaltype'] == 0):
                value = dc.getDayValueByDictionary(self.operatingData)
                dateOfOperation = str(self.operatingData['month'])+"/"+str(self.operatingData['day'])+"/"+str(self.operatingData['year'])
                print("logger.debug: DateOfOperation: " + str(dateOfOperation)) #self.logger.debug("DateOfOperation: " + str(dateOfOperation))
                #self.logger.debug("DateOfOperation: "+str(dateOfOperation))
                return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':value}
            elif (self.operatingData['intervaltype'] == 1):
                value = dc.getMonthValueByDictionary(self.operatingData)
                dateOfOperation = str(self.operatingData['month'])+"/"+str(self.operatingData['year'])
                return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':value}
            elif (self.operatingData['intervaltype'] == 2):
                value = dc.getYearValueByDictionary(self.operatingData)
                dateOfOperation = str(self.operatingData['year'])
                return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':value}
        #except Exception, e:
        except:
            sys_error_info = sys.exc_info()
            print("logger.warn: Error: " + str(sys_error_info))
            #self.logger.warn("Error: "+str(e))

        finally:
            del clippedmask
        mathop = pMath.mathOperations(dict['operationtype'],1,self.operatingData['datatype']['fillValue'],None) 
        if (self.operatingData['intervaltype'] == 0):
            
            dateOfOperation = str(self.operatingData['month'])+"/"+str(self.operatingData['day'])+"/"+str(self.operatingData['year'])
            return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':mathop.getFillValue()}
        elif (self.operatingData['intervaltype'] == 1): 
            dateOfOperation = str(self.operatingData['month'])+"/"+str(self.operatingData['year'])
            return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':mathop.getFillValue()}
        elif (self.operatingData['intervaltype'] == 2):
            dateOfOperation = str(self.operatingData['year'])
            return {"date":dateOfOperation,"epochTime":self.operatingData['epochTime'],'value':mathop.getFillValue()}
    
    def __listen__(self):
        while (True) :
            # KS Refactor 2015 // possible issue where multiple workers are processing the same work items.
            #time.sleep(1)  # Issue may actually be located in the .sh scripts where the workers are created for each head.
            request = json.loads(self.inputreceiver.recv())
            self.operatingData = request
            self.doWork()
        
    def __readMask__(self, uid):
        print("logger.debug: I am reading from temp storage")
        #self.logger.debug("I am reading from temp storage")
        return mst.readHMaskFromTempStorage(uid)
        
    
    def __cleanup__(self):
       
        self.operatingData = None
    
     
    def __init__(self, name, inputconn, outputconn):
        
        # Get the PID to ensure the thread isn't duplicated.
        self.pid = os.getpid()
        
        self.name = name
        self.inputconn = inputconn
        self.outputconn = outputconn

        print("logger.info: Init CHIRPSDataWorker (PID: "+str(self.pid)+" ) : ("+self.name+") listening on "+self.inputconn+" outputting to "+self.outputconn)
        #self.logger.info("Init CHIRPSDataWorker (PID: " + str(self.pid) + " ) : (" + self.name + ") listening on " + self.inputconn + " outputting to " + self.outputconn)

        context = zmq.Context()
        self.inputreceiver = context.socket(zmq.PULL)
        self.inputreceiver.connect(self.inputconn)
        self.outputreceiver = context.socket(zmq.PUSH)
        self.outputreceiver.connect(self.outputconn)
        self.__listen__()
        
        
    def doWork(self):

        print("logger.info: (" + self.name + "):doWork: About to work on request: " + str(self.operatingData))
        #self.logger.info("("+self.name+"):doWork: About to work on request: " +str(self.operatingData))
        
        results = self.__doWork__()
       
        # ks refactor // Understanding how the 'workers' do their work!
        #self.logger.debug("Worker: " +str(self.name)+ " : doWork : Value of results: " + str(results))  
        print("logger.debug: (" + self.name + "):doWork: Value of json.dumps(results): " + str(json.dumps(results))) # self.logger.debug("(" + self.name + "):doWork: Value of json.dumps(results): " + str(json.dumps(results)))
        #self.logger.debug("("+self.name+"):doWork: Value of json.dumps(results): " + str(json.dumps(results)))
        
        results['workid'] = self.operatingData['workid']
        print("logger.debug: Worker (" + self.name + "): " + "Working on " + results['workid']) # self.logger.debug("Worker (" + self.name + "): " + "Working on " + results['workid'])
        #self.logger.debug("Worker ("+self.name+"): "+"Working on "+results['workid'])
        self.outputreceiver.send_string(json.dumps(results))
        self.__cleanup__()
        
if __name__ == "__main__":
    name = sys.argv[1]
    inputconn = sys.argv[2]
    outputconn = sys.argv[3]
    #print("alert 1")
    #logger2 = llog.getNamedLogger("request_processor")
    #logger2.debug("Alert 1")
    ZMQCHIRPSDataWorker(name, inputconn, outputconn)       
        