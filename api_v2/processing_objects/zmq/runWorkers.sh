#!/bin/sh

# Production
#HEADWORKERS=3
#WORKERSPERHEAD=8
# Dev
HEADWORKERS=1 #2
WORKERSPERHEAD=1 #3


# This gives a key error (for _)  This may only be a difference between local dev and prod environment.  This may only be needed in prod environment - since the below stuff works locally.
#python=$(python -c "import os; print(os.environ['_'])")


#CSERV_1.0
# rootdir=/data/data/cserv/pythonCode/servirchirpsdjango #/data/data/cserv/pythonCode/serviringest
#CSERV_2.0 - Prod
# rootdir=/data/data/cserv/pythonCode/servirchirpsdjango #/data/data/cserv/pythonCode/serviringest
#CSERV_2.0 - Dev
rootdir=/Users/ks/ALL/CrisSquared/SoftwareProjects/SERVIR_2020/git_repos/ClimateSERV-2.0-Server/api_v2/processing_objects/zmq

#CSERV_1.0
# BASEIPCDIR="ipc:///tmp/servir/"
#CSERV_2.0 - Prod
# BASEIPCDIR="ipc:///tmp/servir/"
#CSERV_2.0 - Dev
BASEIPCDIR="ipc:///tmp/cserv2_0/"



MAINQUEUEINPUT=${BASEIPCDIR}Q1/input
MAINQUEUEOUTPUT=${BASEIPCDIR}Q1/output


#CSERV_1.0
#PIDNAME=/tmp/servir/pid
#CSERV_2.0 - Prod
#PIDNAME=/tmp/cserv2_0/pid
#CSERV_2.0 - Dev
PIDNAME=/tmp/cserv2_0/pid


cd ${rootdir}
export PYTHONPATH=${PYTHONPATH}:${rootdir}

launch() {
	echo 'python: ' + $python

	# Skipping this - new version won't use Berkley DB, will use python django db
	#python CHIRPS/utils/db/bddbprocessing.py

    # This is where the actual directories are created for the input and output message queues.
	#python CHIRPS/utils/file/fileutils.py /tmp/servir/Q1 input
	#python CHIRPS/utils/file/fileutils.py /tmp/servir/Q1 output
	python legacy/fileutils.py /tmp/cserv2_0/Q1 input
	python legacy/fileutils.py /tmp/cserv2_0/Q1 output

	echo "starting the Head Workers"
	##################Start Input Queue########################################
	#python CHIRPS/processing/zmqconnected/ArgProxyQueue.py ${MAINQUEUEINPUT} ${MAINQUEUEOUTPUT} &
	python legacy/ArgProxyQueue.py ${MAINQUEUEINPUT} ${MAINQUEUEOUTPUT} &
	echo $! > ${PIDNAME}

	##################Start Head Workers and subordinate workers###############
	for i in  $(seq 1 $HEADWORKERS);
	do
		echo 'starting Head Processer'$i

		HEADNAME=HEAD${i}
		echo "Starting Head Worker Named:" $HEADNAME

		#python CHIRPS/utils/file/fileutils.py /tmp/servir/${HEADNAME} q1in
		#python CHIRPS/utils/file/fileutils.py /tmp/servir/${HEADNAME} q1out
		#python CHIRPS/utils/file/fileutils.py /tmp/servir/${HEADNAME} q2in
		#python CHIRPS/utils/file/fileutils.py /tmp/servir/${HEADNAME} q2out
		python legacy/fileutils.py /tmp/cserv2_0/${HEADNAME} q1in
		python legacy/fileutils.py /tmp/cserv2_0/${HEADNAME} q1out
		python legacy/fileutils.py /tmp/cserv2_0/${HEADNAME} q2in
		python legacy/fileutils.py /tmp/cserv2_0/${HEADNAME} q2out

		HEADQUEUEONEINPUT=${BASEIPCDIR}${HEADNAME}'/q1in'
		HEADQUEUEONEOUTPUT=${BASEIPCDIR}${HEADNAME}'/q1out'
		HEADQUEUETWOINPUT=${BASEIPCDIR}${HEADNAME}'/q2in'
		HEADQUEUETWOOUTPUT=${BASEIPCDIR}${HEADNAME}'/q2out'


		#python CHIRPS/processing/zmqconnected/ZMQCHIRPSHeadProcessor.py ${HEADNAME} ${MAINQUEUEOUTPUT} ${HEADQUEUEONEINPUT} ${HEADQUEUETWOOUTPUT} &
		python legacy/ZMQCHIRPSHeadProcessor.py ${HEADNAME} ${MAINQUEUEOUTPUT} ${HEADQUEUEONEINPUT} ${HEADQUEUETWOOUTPUT} &
		echo $! >> ${PIDNAME}

		#python CHIRPS/processing/zmqconnected/ArgProxyQueue.py ${HEADQUEUEONEINPUT} ${HEADQUEUEONEOUTPUT} &
		python legacy/ArgProxyQueue.py ${HEADQUEUEONEINPUT} ${HEADQUEUEONEOUTPUT} &

		value=$!
		echo ${value} >> ${PIDNAME}
		for  j in $(seq 1 $WORKERSPERHEAD);
		do
			WORKERNAME=W${j}${HEADNAME}
			echo "Starting Worker: $WORKERNAME"

			#python CHIRPS/processing/zmqconnected/ZMQCHIRPSDataWorker.py ${WORKERNAME} ${HEADQUEUEONEOUTPUT} ${HEADQUEUETWOINPUT}  &
			python legacy/ZMQCHIRPSDataWorker.py ${WORKERNAME} ${HEADQUEUEONEOUTPUT} ${HEADQUEUETWOINPUT}  &

			echo $! >> ${PIDNAME}
		done

		#python CHIRPS/processing/zmqconnected/ArgProxyQueue.py ${HEADQUEUETWOINPUT} ${HEADQUEUETWOOUTPUT} &
		python legacy/ArgProxyQueue.py ${HEADQUEUETWOINPUT} ${HEADQUEUETWOOUTPUT} &
		echo $! >> ${PIDNAME}

	done

	#python CHIRPS/utils/file/filePermissions.py /tmp/servir/Q1/input
	python legacy/filePermissions.py /tmp/cserv2_0/Q1/input
}

start() {
	if [ -f $PIDNAME ] && kill -0 $(cat $PIDNAME); then
    	echo 'Service already running' >&2
    	return 1
  	fi
  	echo 'Starting service' >&2
	launch
  	echo 'Service started' >&2
}

stop() {
	if [ ! -f "$PIDNAME" ] || ! kill -0 $(cat "$PIDNAME"); then
    	echo 'Service not running' >&2
    	return 1
  	fi
  	echo 'Stopping service' >&2
  	kill -15 $(cat "$PIDNAME") && rm -f "$PIDNAME"
 	 echo 'Service stopped' >&2
}



case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
esac
