import os, shutil
from re import L
import tkinter as tk
import tkinter.filedialog as fd
from time import sleep
from makeJson import jsonData
from functions import yesNo

root = tk.Tk()
root.withdraw()

# create folder structure
def folderStructure(path):
    try:
        newDir = f'{path}\GVO\MIBs'
        print(newDir)
        os.makedirs(newDir)
        #OS ERROR HERE
    except OSError as e:
        print ("Error: Creation of the directory %s failed" % newDir)
        print (e)

# select inputFile
def inputFile():
    types=[('RollSNMP(*.rsnmp)','*.rsnmp')]
    fullFile = fd.askopenfilename(title='Select files...', filetypes=types)
    if fullFile == '': inputFile=False
    else:
        parts = fullFile.split('/')
        inputFile={'fileName':parts[-1],'filePath':'\\'.join(parts[:-1]), 'fullPath':fullFile}
    return inputFile

# collect required MIBs
def getMIBs(path):
    # get a list of files?
    mibsNeeded=yesNo('Are separate MIB files required?', default='yes')
    if mibsNeeded==True:
        getFiles=fd.askopenfilenames(title='Select MIBs...')
        if getFiles == '': mibsList='empty files list'
        else:
            mibsList=[]
            for a in getFiles:
                b=a.split(', ')
                mibsList.extend(b)
        # check list is not empty
        if mibsList == 'empty files list':
            print('Error - no MIBs selected.')
        else:
            # copy drivers to \GVO\MIB location
            for item in mibsList:
                shutil.copy(item, os.path.join(f'{path}\GVO\MIBs'))
    else: return

# convert *.rsnmp to GVO version and copy to location
def convertSNMP(driver, path):
    with open(driver, 'r') as f:
        lines = f.readlines()
        search = '<MIBSource path='
        
        matchLines = []
        i=0
        
        for line in lines:
            if search in line:
                matchLines. insert(i, line)
            
        f.close()
        
    # if list is empty, print error
    if len(matchLines)==0:
        MIBSource=False
        error = 'Error: MIB source path not detected'
    # if list == 1 extract mib source path data
    elif len(matchLines)==1:
            # read in string
            s0=''.join(matchLines[0])
            # split at ", grab the path
            s1=s0.split('\"')
            s2=s1[1]
            # split at \
            s3=s2.split('\\')
            # create new MIB source, remving 'SNMP Library' entry
            s4=s3[1:]
            s5='/'.join(s4)
            MIBSource = f'\t<MIBSource path="{s5}"/>'
    # catch multiple entries
    else:
        MIBSource=False
        error = 'Error: multiple MIBSource entries'
        
    if MIBSource != False:
        # replace original matchLines[0] with new MIBSource
        with open(driver, 'r') as f:
            fileData = f.read()
            f.close()
        fileData = fileData.replace(matchLines[0], MIBSource)
        
        # grab driver name
        name=driver.split('/')
        # write new driver
        with open(f'{path}\GVO\{name[-1]}', 'w') as f:
            f.write(fileData)
            f.close()
    
    # handle errors
    else: print(error)

# TODO
# convert and collect dependant drivers
# zip up into package

# main
if __name__ == "__main__":
    driverFile = inputFile()
    if driverFile!=False:
        folderStructure(driverFile['filePath'])
        getMIBs(driverFile['filePath'])
        convertSNMP(driverFile['fullPath'], driverFile['filePath'])
        jsonData(driverFile['fullPath'], driverFile['filePath'])
    else:
        print('User cancelled operation.')
        sleep(2)