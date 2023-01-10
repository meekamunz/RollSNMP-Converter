import json
import tkinter as tk
import tkinter.filedialog as fd
from functions import yesNo

root = tk.Tk()
root.withdraw()

# setDriverVersion
def setDriverVersion(inputFile):
    with open(inputFile, 'r') as file:
        lines = file.readlines()
        search = 'StaticString'
        
        matchLines = []
        i=0
        
        # find lines matching search, add to list
        for line in lines:
            if search in line:
                matchLines.insert(i, line)
                i += 1
        
        file.close()
        
    # if list is empty, set driverVersion=0.0.1 indicating no driver version detected
    if len(matchLines)==0:
        driverVersion='0.0.1'
        
    # set driverVersion to match SVN check-in number
    elif len(matchLines)==1:
        # read in string
        s0=''.join(matchLines[0])
        # split at '.rsnmp '
        s1=s0.split('.rsnmp ')
        # split at ' '
        s2=''.join(s1[1])
        s3=s2.split(' ')
        # grab the svn version number
        svnVersion=s3[0]
        # set the driver version number
        driverVersion=svnVersion+'.0.0'
        
    # catch multiple entries, set driverVersion=0.0.9 to indicate multiple candidates for driver version
    else:
        driverVersion='0.0.9'
        
    return driverVersion

# setIncludes
def setIncludes(inputFile):
    l0=inputFile.split('\\')
    # handle dependant drivers
    dependCheck = yesNo('Are there any dependant RollSNMP drivers?', default='no')
    if dependCheck==True:
        l1=fd.askopenfilenames(title='Select files...')
        l2 = list(l1)
        l3=[]
        for a in l2:
            b=a.split('/')
            l3.append(b[-1])
        l4=l0[-1].split('/')
        # needs each entry quoted, so leave as list
        includes = l3+l4
    
    else:
        # return includes as a list
        includes = [l0[-1]]
    
    return includes

# setManufacturer
def setManufacturer(inputFile):
    l0=inputFile.split('\\')
    
    # get 'SNMP Library' position
    if 'SNMP Library' in l0: libraryPos=l0.index('SNMP Library')
    else: return 'Error: Manufacturer - no \'SNMP Library\' in path.'
    
    # move to manufacturer position and return manufacturer
    manufacturer = l0[libraryPos+1]
    return manufacturer

# setDriverName
def setDriverName(inputFile):
    with open(inputFile, 'r') as file:
        lines = file.readlines()
        search = '<UnitTypeDef'
        
        matchLines = []
        i = 0
        
        # find lines matching search, add to list
        for line in lines:
            if search in line:
                matchLines.insert(i, line)
                i += 1
            
        file.close()
            
        flag=False
        # if list is empty or greater than 1, set driverName to file path
        if len(matchLines)==0: flag=True
        
        elif len(matchLines)>1: flag=True
        
        if flag==True:
            l0=inputFile.split('\\')
            
            # get XML position
            if 'XML' in l0: xmlPos=l0.index('XML')
            elif 'xml' in l0: xmlPos=l0.index('xml')
            else: return 'Error: Driver Name - no XML in path.'
            
            # move to manufacturer position and return manufacturer
            driverName = l0[xmlPos-1]
            
        # set driverName to match <UnitTypeDef> entry
        else:
            # read in string
            s0=''.join(matchLines[0])
            # split at 'typeName='
            s1=s0.split('typeName=')
            # split at 'snmpVersion'
            s2=''.join(s1[1])
            s3=s2.split('\"')
            # remove quotes and return driverName
            driverName=s3[1].strip('\"')
            
        return driverName

# build json
def jsonData(inputFile, path):
    includes=setIncludes(inputFile)
    manufacturer=setManufacturer(inputFile)
    driverName=setDriverName(inputFile)
    driverVersion=setDriverVersion(inputFile)
    dict = {'includes':includes, 'manufacturer':manufacturer, 'driverName':driverName, 'driverVersion':driverVersion, 'deviceName':f'{manufacturer} - {driverName}'}
    jsonString=json.dumps(dict, indent=4)
    f = open(f'{path}\driver.json', 'w')
    f.write(jsonString)
    f.close