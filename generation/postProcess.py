#!/usr/bin/env python

# unzip LHE files in a folder
# calculate the XS of the samples in a generation
# verify the integrity of all LHE files
# compare the number of generated events present in the lhe file to the ones reported in the log
# prepare list of files for CFG file
# if asked, remove log files


import sys
import fnmatch
import os
import subprocess
import argparse 
from math import sqrt 
import glob


usual_errors = []
usual_errors.append ('stty: standard input: Inappropriate ioctl for device')



def readCondorReport (path):
    lista = glob.glob (path+ '/*.log')
#    print (lista)
    if len (lista) > 1:
        print ('too many log files, exiting\n')
        sys.exit (1)
    filename = lista[0]
 #   print (filename)
    normal = 0
    endcodes = []
    jobID = '-1'
    endcode = '-1'
    runtime = '00:00:00'
    with open (filename, 'r') as f :
        linecount = 5
        for line in f.readlines () :
            linecount += 1
            if 'Job terminated' in line :
                linecount = 0
                jobID =  line.split ()[1][1:-1].split ('.')[1]
            if linecount == 1 :
                if 'Abnormal' in line :
                  endcode = line.split ()[4][:-1]
                else :
                  endcode = line.split ()[5][:-1]
                if endcode == '0' : normal += 1
            if linecount == 2 :
                runtime = line.split ()[2][:-1]
            if linecount == 3 :    
                endcodes.append ([jobID, endcode, runtime])                 
                jobID = '-1'
                endcode = '-1'
                runtime = '00:00:00'

#    print endcodes
#    print len (endcodes)
#    print ('normally terminated', normal)
    return endcodes
    
  
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


# check whether in the err file there are unexpected errors,
# or solely some known irrelevant ones,
# listed in usual_errors
# True = there is a problem
# False = everything is OK
def errFileHasIssues (filename):
    counter = 0
    with open (filename, 'r') as file:
        for line in file:
            known = 0
            for err in usual_errors:
                if err in line: 
                    known = 1
                    break
            if known == 1: continue
            counter = counter + 1
    if counter > 0: return [True, filename.split('.')[-2], filename]
    return [False, filename.split('.')[-2], filename]
  

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


# get the list of files ending with the "pattern"
# in the folder "basefolder",
# if the file name does not contain any of the ID's
# listed in "discard"
def getFilesList (basefolder, pattern, discard):
    matches = []
    myfilenames = []
    for root, dirnames, filenames in os.walk (basefolder):
        for filename in fnmatch.filter (filenames, pattern):
            fullname = os.path.join (root, filename)
            count = 0
            for elem in discard:
                if ('.'+elem+'.' in fullname) or ('_'+elem+'/' in fullname): 
                    count = 1
                    break
            if count > 0 : continue
            matches.append (os.path.join (os.getcwd (), root, filename))
            myfilenames.append (filename)
    return [matches, myfilenames]        


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


def countEvents (filename):
    objFile = open (filename, 'r')
    return objFile.read ().count("<event>")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


def checkClosure (filename):
    objFile = open (filename, 'r')
    fileContent = objFile.read ().split ()
    return (fileContent[-1] == "</LesHouchesEvents>")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


def findXS (filename):
    objFile = open (filename, 'r')
    fileContent = objFile.read ().split ()
    return fileContent[-4]


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


def findXSwE (filename):
    XSline = ''
    Nline = ''
    with open(filename, 'r') as file:
        counter = 0
        for line in file:
            if counter > 0:
                Nline = line
                break
            if 'Cross-section' in line:
                XSline = line
                counter = counter + 1
    crossSection = float (XSline.split ()[2])
    crossSectionError = float (XSline.split ()[4])
    numberOfEvents = int (Nline.split ()[4])
    return (crossSection, crossSectionError, numberOfEvents)


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


# this function runs on a list of outputs
# of the findXSwE function,
# i.e. a list of tuples
# from the tuples the relavant info is the XS and the XS uncertainty
def calcTotXS (singleGenInfoList):
#    XSs = [info[0] for info in singleGenInfoList] # single cross sections
#    Ws = [ 1. / (info[1] * info[1]) for info in singleGenInfoList] # weights
#    sumW = sum (Ws)

    XS = sum (x / (e*e) for x, e, n in singleGenInfoList)
    sumW = sum (1. / (e*e) for x, e, n in singleGenInfoList)
    print singleGenInfoList


    #if not sumW < 0.0001:
    print (XS)
    print (sumW)

    XS = XS / sumW
    XSe = sqrt (1. / sumW)
   # else:
   #     raise ZeroDivisionError
   # else:
   #     print('SM case or sumW equal to zero replacing XS by known SM value')
    return [XS, XSe]


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


def makeNtupleProdCfg (basefolder,outfolder, LHEfiles, XS):

    processName = basefolder.split ('/')[-1]
    processName = processName.replace ('_results', '')

##    configFileName = basefolder + '/read_03_input.cfg'
    configFileName = 'gen/'+ processName + '_results/read_03_input.cfg'    
#    configFileName = processName + '_results/read_03_input.cfg'    

    outf = open (configFileName, 'w')

    outf.write ('[general]\n')
    outf.write ('samples = ' + processName + '\n')
#    outf.write ('variables = mjj, mll, ptj1, ptj2, etaj1, etaj2, phij1, phij2, ptl1, ptl2, ptZZ, etal1, etal2, met, ptll, ptemuplus, ptemuminus, deltaetajj, deltaphijj, m4l, m4ljj, ptZ, ptee, ptmumu, mee, mmumu\n')
#    outf.write ('variables = mjj, mll, ptj1, ptj2, etaj1, etaj2, phij1, phij2, ptl1, ptl2, etal1, etal2, met, ptll, deltaetajj, deltaphijj, m4l, m4ljj, ptZ, ptee, ptmumu, mee, mmumu\n')
##CT: new variables ptRel added
#    outf.write ('variables = mjj, mll, ptj1, ptj2, etaj1, etaj2, phij1, phij2, ptl1, ptl2, etal1, etal2, met, ptll, deltaetajj, deltaphijj, m4l, m4ljj, ptZ, ptee, ptmumu, mee, mmumu, ptl1RelZZ, ptl2RelZZ, ptj1RelZZ, ptj2RelZZ, pteeRelZZ, ptl1RelZ1, ptl2RelZ1, ptj1RelZ1, ptj2RelZ1, ptl1RelZ2, ptl2RelZ2, ptj1RelZ2, ptj2RelZ2, ptZ1RelZ2, ptVRelZ1, ptVRelZ2, ptV, ptemuplus, ptemuminus\n')
#CT: new variables FWM added
#    outf.write ('variables = mjj, mll, ptj1, ptj2, etaj1, etaj2, phij1, phij2, ptl1, ptl2, etal1, etal2, met, ptll, deltaetajj, deltaphijj, m4l, m4ljj, ptZ, ptee, ptmumu, mee, mmumu, ptl1RelZZ, ptl2RelZZ, ptj1RelZZ, ptj2RelZZ, pteeRelZZ, ptl1RelZ1, ptl2RelZ1, ptj1RelZ1, ptj2RelZ1, ptl1RelZ2, ptl2RelZ2, ptj1RelZ2, ptj2RelZ2, ptZ1RelZ2, ptVRelZ1, ptVRelZ2, ptV, ptemuplus, ptemuminus, H0sjj, H0tjj, H0zjj, H1sjj, H1tjj, H1zjj, H2sjj, H2tjj, H2zjj, H0sll, H0tll, H0zll, H1sll, H1tll, H1zll, H2sll, H2tll, H2zll, H6tjj, H6tll, TotH0s, TotH0t, TotH0z, TotH1s, TotH1t, TotH1z, TotH2s, TotH2t, TotH2z, TotH6t\n')
    
    myVars ='mll, ptl1, ptl2, etal1, etal2, ptll, ptZ, ptl1RelZ1, ptl2RelZ1, TotH0s, TotH0t, TotH0z, TotH1s, TotH1t, TotH1z, TotH2s, TotH2t, TotH2z, TotH6t, H0sll, H0tll, H0zll, H1sll, H1tll, H1zll, H2sll, H2tll, H2zll, H6tll'
    if processName.startswith('ZZ'):
        myVars+=', m4l, ptee, ptmumu, mee, mmumu, ptl1RelZZ, ptl2RelZZ, pteeRelZZ, ptl1RelZ2, ptl2RelZ2, ptZ1RelZ2, ptemuplus, ptemuminus' 
    if processName.startswith('ZZ2e2mu') or processName.startswith('VZ'): 
        myVars+=', mjj, ptj1, ptj2, etaj1, etaj2, phij1, phij2, deltaetajj, deltaphijj, ptj1RelZ1, ptj2RelZ1, ptV, ptVRelZ1, H0sjj, H0tjj, H0zjj, H1sjj, H1tjj, H1zjj, H2sjj, H2tjj, H2zjj,H6tjj' 
    if processName.startswith('ZZ2e2mu'): 
        myVars+=', m4ljj, ptj1RelZZ, ptj2RelZZ, ptj1RelZ2, ptj2RelZ2, ptVRelZ2, ptVRelZZ' 
    if processName.startswith('ZZG') or processName.startswith('VZG') or processName.startswith('WZG'): 
        myVars+=', ptGamma, etaGamma, phiGamma, ptGRelZ1' 
    if processName.startswith('ZZG'):
        myVars+=', ptGRelZZ' 
    if processName.startswith('WZG'): 
        myVars+=', ptW, met, ptl1RelWZ, ptl2RelWZ, ptl1RelW, ptl2RelW, ptWRelZ, ptWRelG, mWlept, mtWlept'
    if processName.startswith('VZG'): 
        myVars+=', ptl1RelG, ptl2RelG, ptj1RelG, ptj2RelG, ptGRelV, ptGRelVZ, ptjjRelZG' 

#CT:TESTME: apparently completed for all the triboson channel

    outf.write ('variables = '+myVars+'\n')

    outf.write ('outputFile = '+ outfolder +'/ntuple_' + processName + '.root\n')
    outf.write ('applycuts = true\n')
    outf.write ('\n')
    outf.write ('[' + processName + ']\n')
    outf.write ('XS = ' + XS + '\n')
    outf.write ('# pb\n')
    outf.write ('files = ' + LHEfiles + '\n')

    outf.close ()

    print (configFileName + ' generated\n')


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 


if __name__ == '__main__':


    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False, help='debugging mode')
    parser.add_argument("-b", "--basefolder", action="store", type=str, help="base folder of the input files")
    parser.add_argument("-t", "--task", action="store", type=str, default="" , help="choose a specific task: check, clean, unzip, rezip; optional, otherwise all except 'clean' are performed")
    parser.add_argument("-o", "--outNtuple", action="store", type=str, default="basefolder", help="output directory for the ntuples created by read_03.cpp")


    args = parser.parse_args()

    DEBUG = args.debug
    basefolder = args.basefolder
    outfolderNtuple = args.outNtuple
    task = args.task #task is optional, default "", doing all the task except for clean

    print ('folder:\t', basefolder)
    print ('---------------------------------------------')

    
    if "check" in task:
        print ('checking errors\n')
        files_err = getFilesList (basefolder, '*.err', [])
        issues = [errFileHasIssues (file) for file in files_err[0]]
        discard = [ID for prob, ID, filename in issues if prob == True]
        for elem in discard: print ('ignoring job ' + elem)
        sys.exit (0)
      
    elif "clean" in task:
        print ('cleaning folder ' + basefolder + ' from job reports...\n')
        postprocess_file = getFilesList (basefolder, 'postProcess.txt', [])
        if (len (postprocess_file[0]) == 0):
            print 'no postProcess.txt file found, quitting\n'
            sys.exit (0)

         # remove the .out and .err only for successful jobs
        files_err = getFilesList (basefolder, '*.err', [])
        issues = [errFileHasIssues (file) for file in files_err[0]]
        removeError = [filename for prob, ID, filename in issues if prob == False]
        for file in removeError: os.remove (file)
        removeOutput = [filename.replace ('.err','.out') for filename in removeError]
        for file in removeOutput: os.remove (file)

    elif "unzip" in task:
        print ('unzipping...')
        os.system ('for fil in  `find  ' + basefolder + ' -name \"*gz\"` ; do gunzip $fil ; done')
        sys.exit (0)
 
    elif "rezip" in task:
        files_lhe = getFilesList (basefolder, '*.lhe', [])
        for filename in files_lhe[0] : 
            print ('gzip ' + filename)
            subprocess.call (['gzip', str (filename)])
        sys.exit (0)

    #Now doing the normal code
    if "basefolder" in outfolderNtuple:  #default: the output folder is the same as the input one
        outfolderNtuple = args.basefolder
        if DEBUG: print "Default output folder : ", outfolderNtuple   


    # FIXME use the numbers to discard failed jobs
    # FIXME make a histogram of the time duration of jobs
    #readCondorReport (basefolder)

    # collect the list of err files
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    print ('reading folder ' + basefolder + '\n')

    print ('checking error reports...')
    files_err = getFilesList (basefolder, '*.err', [])
    issues = [errFileHasIssues (file) for file in files_err[0]]
    discard = [ID for prob, ID, filename in issues if prob == True]

    print ('checking not finished runs...')
    files_run = getFilesList (basefolder, '*running', [])
    discard = discard + [name.split ('_')[3] for name in files_run[1]]

    discard = []

    for elem in discard: print ('ignoring job ' + elem)

    # unzip LHE files
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    print ('unzipping...')
    # https://linuxhandbook.com/execute-shell-command-python/
    os.system ('for fil in  `find  ' + basefolder + ' -name \"*gz\"` ; do gunzip $fil ; done')
    
    # check lhe files integrity
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    print ('checking LHE files integrity...')
    files_lhe = getFilesList (basefolder, '*.lhe', discard)

    print (files_lhe)

    closure = [checkClosure (file) for file in files_lhe[0]]

    allOK = 0
    for i in range (len (closure)):
        if (closure[i] == False):
            print (files_lhe[1] + 'not properly closed')
            allOK = allOK + 1
    if allOK > 0: 
        print ('found ' + allOK + ' files not properly closed')
    else:
        print ('all files closed regularly') 

    if DEBUG: 
        print ('\nLIST OF LHE FILES:')
        print (','.join (files_lhe[0]))
        print ('\n')

    # get number of events from LHE files
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    # this returns a list with the same elements found in findWSwE, but with different ordering
#    NB = [int (countEvents (file)) for file in files_lhe[0]]

    # add final report to the results folder
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    files_out = getFilesList (basefolder, '*.out', discard)
#    print (files_out)

    XSs = [findXSwE (file) for file in files_out[0]]

    totXS = calcTotXS (XSs)
    print ('average XS: ' + str (totXS[0]) + ' +- ' + str (totXS[1]) + ' pb')
    print ('average XS: ' + str (1000. * totXS[0]) + ' +- ' + str (1000. * totXS[1]) + ' fb')

    outputfile = open (basefolder+'postProcess.txt' ,'w')
    ##outputfile = open ('postProcess.txt' ,'w')
    outputfile.write ('average XS: ' + str (totXS[0]) + ' +- ' + str (totXS[1]) + ' pb\n')
    outputfile.write ('average XS: ' + str (1000. * totXS[0]) + ' +- ' + str (1000. * totXS[1]) + ' fb\n\n')
    outputfile.write ('LHE files list:\n' + ','.join (files_lhe[0]) + '\n')
    outputfile.close ()

    # add cfg file for read_03 to the results folder
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    makeNtupleProdCfg (basefolder,outfolderNtuple, ','.join (files_lhe[0]), str (totXS[0]))
    #makeNtupleProdCfg (basefolder,outfolderNtuple, ','.join (files_lhe[0]), "dummy")

