import os
import tkinter as tk
import tkinter.filedialog as fd
from makeJson import jsonData

root = tk.Tk()
root.withdraw()

# create folder structure
def folderStructure(path):
    try:
        fullpath = path+'\GVO\MIBs'
        print(fullpath)
        os.mkdir(fullpath)
        #OS ERROR HERE
    except OSError:
        print ("Creation of the directory %s failed" % fullpath)
    else:
        print ("Successfully created the directory %s " % fullpath)


# select inputFile
def inputFile():
    types=[('RollSNMP(*.rsnmp)','*.rsnmp')]
    fullFile = fd.askopenfilename(title='Select files...', filetypes=types)
    if fullFile == '': inputFile=False
    else:
        parts = fullFile.split('/')
        inputFile={'fileName':parts[-1],'filePath':'\\'.join(parts[:-1])}
    return inputFile
    

# create JSON file


# collect required MIBs


# convert *.rsnmp to GVO version

# zip up into package

# main
if __name__ == "__main__":
    driverFile = inputFile()
    folderStructure(driverFile['filePath'])
    #THIS WORKS
    #jsonData(driverFile['filePath']+'\\'+driverFile['fileName'])