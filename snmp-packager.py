import os, shutil, json, re
import tkinter as tk
import tkinter.filedialog as fd
from pathlib import Path
from time import sleep
from makeJson import jsonData
from functions import yesNo

root = tk.Tk()
root.withdraw()

MIB_SOURCE_REGEX = r'<MIBSource.*href=".*?".*?>'

GLOBAL_TRANSLATION_DEF_LINK_REGEX = r'<GlobalTranslationDef.*link="(.*?)".*?>'
TRANSLATION_DEF_LINK_REGEX = r'(<TranslationDef.*link=")(.*?)(".*?>)'

# create folder structure
def folderStructure(path, name):
    try:
        newDir = f'{path}\GVO\{name}\MIBs'
        os.makedirs(newDir)
    except OSError as e:
        print ("Error: Creation of the directory %s failed" % newDir)
        print (e)

# copy driver to GVO dir
def copyDriver(driver, path, name):
    shutil.copy(driver, os.path.join(f'{path}\GVO\{name}'))

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
def getMIBs(path, name):
    # get a list of files?
    print('Select MIB files...')
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
            shutil.copy(item, os.path.join(f'{path}\GVO\{name}\MIBs'))

# convert *.rsnmp to GVO version and copy to GVO location
def convertSNMP(driver, path, driverName):

    # grab driver name
    n0=driver.split('/')
    n1=n0[-1]
    n2=n1.split('.')
    name=n2[0]

    print(f'Converting {driver}...')
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
        error = 'WARN: MIB source path not detected, original file used'
        # copy the file anyway incase this is correct
        parts = driver.split('/')
        shutil.copy(driver, os.path.join(f'{path}\GVO\{parts[-1]}'))
    # if list == 1 extract mib source path data
    elif len(matchLines)==1:
        # not sure if original path is correct, should it be manufacturer/MIBs, or driverName/MIBs?
        ## read in string
        #s0=''.join(matchLines[0])
        ## split at ", grab the path
        #s1=s0.split('\"')
        #s2=s1[1]
        ## split at \
        #s3=s2.split('\\')
        ## create new MIB source, remving 'SNMP Library' entry
        #s4=s3[1:]
        #s5='/'.join(s4)
        #MIBSource = f'/t<MIBSource path="{s5}"/>'
        MIBSource = f'/t<MIBSource path="{name}/MIBs"/>'
    # catch multiple entries
    else:
        MIBSource=False
        error = f'Error: multiple MIBSource entries: {matchLines}'
        
    if MIBSource != False:
        # replace original matchLines[0] with new MIBSource
        with open(driver, 'r') as f:
            fileData = f.read()
            f.close()
        fileData = fileData.replace(matchLines[0], MIBSource)
        
        # grab driver name
        name=driver.split('/')
        # write new driver
        with open(f'{path}\GVO\{driverName}\{name[-1]}', 'w') as f:
            f.write(fileData)
            f.close()
        print('Complete')
        
    
    # handle errors
    else:
        print(f'{driver} not converted, please check error message')
        print(error)

# gather list of included drivers
# assumes that included drivers are in the same path as main driver
def checkIncludes(path):
    f = open(f'{path}\driver.json')
    data = json.load(f)
    includes=[]
    if isinstance(data['includes'], list)==True: includes.extend(data['includes'][:-1])
            
    if len(includes) == 0: includes=False
    f.close
    return includes

# zip up into package
def zipup(path, driver):
    os.chdir(f'{path}\GVO\\')
    shutil.make_archive(driver, 'zip', f'{path}\GVO\{driver}')
    # remove unzipped version
    shutil.rmtree(f'{path}\GVO\{driver}')

# main
if __name__ == "__main__":
    loop=True
    while loop:
        driverFile = inputFile()
        s=[]
        s=driverFile['fileName'].split('.')
        driverName=s[0]
        if driverFile!=False:
            folderStructure(driverFile['filePath'], driverName)
            getMIBs(driverFile['filePath'], driverName)
            copyDriver(driverFile['fullPath'], driverFile['filePath'], driverName)

            # convert driver to GVO
            convertSNMP(driverFile['fullPath'], driverFile['filePath'], driverName)
            
            # create gvo driver file full path & fill location
            gvoDriver=driverFile['filePath']+'\\GVO\\'+driverName+'\\'+driverFile['fileName']
            gvoDriverLoc=driverFile['filePath']+'\\GVO\\'+driverName

            # create driver.json
            jsonData(gvoDriver, gvoDriverLoc)

            # move any dependant drivers
            includes=checkIncludes(gvoDriverLoc)
            if includes != False:
                # move included drivers
                for i in includes:
                    copyDriver(driverFile['filePath']+'\\'+i, driverFile['filePath'], driverName)

            zipup(driverFile['filePath'], driverName)
        else:
            print('User cancelled operation.')
            sleep(2)
        repeat=yesNo('Convert another driver?', default="no")
        loop=repeat