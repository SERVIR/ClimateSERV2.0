'''
Created on Mar 1, 2015

@author: jeburks
'''
import os
import sys

def makeFileGroupReadable(filename):

    #print "Changing Permissions:",filename
    #os.chmod(filename, 0766) # Python 3 now requires '0o' infront of the octal literals (so 0o in front of 0766)

    print("Changing Permissions: " + str(filename))
    os.chmod(filename, 0o0766)

if __name__ == '__main__':
    makeFileGroupReadable(sys.argv[1])