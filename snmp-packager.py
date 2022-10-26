import os, shutil, json
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
            shutil.copy(item, os.path.join(f'{path}\GVO\MIBs'))
            print(f'{item} copied to {path}\GVO\MIBs\{item}')

# convert *.rsnmp to GVO version and copy to GVO location
# chris has done the MIBSource change, just need to do the move
def convertSNMP(driver, path):

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
        with open(f'{path}\GVO\{name[-1]}', 'w') as f:
            f.write(fileData)
            f.close()
        print('Complete')
    
    # handle errors
    else:
        print(f'{driver} not converted, please check error message')
        print(error)

# gather included drivers
# assumes that included drivers are in the same path as main driver
def checkIncludes(path):
    f = open(f'{path}\GVO\driver.json')
    data = json.load(f)
    includes=[]
    for a in data['includes']:
        b=a.split(', ')
        includes.extend(b[:-1])

    if len(includes) == 0: includes=False
    
    return includes

# zip up into package
def zipup(path, driver):
    # remove '.rsnmp' from driver name
    s=[]
    s=driver.split('.')
    name=s[0]

    # make 'name' directory
    os.mkdir(f'{path}/GVO/{name}')

    # copy GVO folder content to new folder 'name'
    src_dir=f'{path}/GVO/'
    dst_dir=f'{path}/GVO/{name}/'

    fileNames=os.listdir(src_dir)

    for f in fileNames:
        try:
            shutil.move(os.path.join(src_dir+f), os.path.join(dst_dir+f))
        except: continue

    # zip up
    os.chdir(f'{path}\GVO')
    shutil.make_archive(name, 'zip', f'{path}\GVO\{name}')

    # remove unzipped version
    shutil.rmtree(f'{path}\GVO\{name}')

# main
if __name__ == "__main__":
    loop=True
    while loop:
        driverFile = inputFile()
        if driverFile!=False:
            folderStructure(driverFile['filePath'])
            getMIBs(driverFile['filePath'])
            convertSNMP(driverFile['fullPath'], driverFile['filePath'])
            jsonData(driverFile['fullPath'], driverFile['filePath'])
            includes=checkIncludes(driverFile['filePath'])
            if includes != False:
                # included drivers moved, convert drivers
                for i in includes:
                    driver=f'{driverFile["filePath"]}/{i}'
                    driver.replace('\\', '/')
                    outputPath=f'{driverFile["filePath"]}'
                    convertSNMP(driver, outputPath)
            zipup(driverFile['filePath'], driverFile['fileName'])
        else:
            print('User cancelled operation.')
            sleep(2)
        repeat=yesNo('Convert another driver?', default="no")
        loop=repeat