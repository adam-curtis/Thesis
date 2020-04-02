
import sys
import arcpy
import os
from pathlib import Path
print("Got here")
def averageFields(fieldsArray):
    test = []
    for i in fieldsArray:
        if i != 'None':
            test.append(float(i))
    if len(test) == 0:
        return None
    else:
        return sum(test)/len(test)

def calculateFieldsArray(files):
    fieldsArray = []
    for file in files:
        fileName = Path(file).stem
        totalBands = arcpy.Describe(os.path.splitext(file)[0])
        totalBands = totalBands.bandCount
        if(totalBands == 1):
            fieldsArray.append('!'+fileName+'!')
        else:
            for d in range(1,totalBands+1):
                fieldsArray.append('!b'+str(d)+'_'+fileName+'!')
    return fieldsArray

def calculateBandsArray(files):
    bandsArray = []
    for file in files:
        fileName = Path(file).stem
        totalBands = arcpy.Describe(os.path.splitext(file)[0])
        totalBands = totalBands.bandCount
        for i in range(1,totalBands+1):
            bandsArray.append(fileName+'/Band_'+str(i))
    return bandsArray

projectFilePath = sys.argv[1]
country = sys.argv[2]
date = sys.argv[3]
sys.stdout.write(projectFilePath + '\n')
sys.stdout.write(country + '\n')
sys.stdout.write(date + '\n')
tifFiles = projectFilePath + '\\TIFS'
projDB = country +".gdb"
projectedGeoTiffDB =projectFilePath + "\\" + projDB
frontEndPath = projectFilePath[:projectFilePath.rfind("/")]
aprx = arcpy.mp.ArcGISProject(frontEndPath + r"\CopyProject.aprx")
aprx.saveACopy(projectFilePath+"\\"+country+".aprx")
aprx = arcpy.mp.ArcGISProject(projectFilePath+"\\"+country+".aprx")

#Creates File Geodatabase for the reprojected geoTiffs
if not arcpy.Exists(projectedGeoTiffDB):
    arcpy.CreateFileGDB_management(projectFilePath,projDB)
 
arcpy.env.workspace = projectedGeoTiffDB
aprx.defaultGeodatabase = projectedGeoTiffDB

fileList = dict();          
for subdir, dirs, files in os.walk(tifFiles):
    for file in files:
        if file.endswith(".tif"):
            fileList[file] = []
print(fileList) 
for subdir, dirs, files in os.walk(tifFiles):
     for file in files:
         if file.endswith(".tif"):
             currTile = subdir.split("\\")[-1]
             fileID = file[9:16]
             filePath = subdir + "\\" + file
             projectedGeoTiff = projectedGeoTiffDB + "\\" + currTile + "_" + fileID
             if not (arcpy.Exists(projectedGeoTiff)):
                 arcpy.ProjectRaster_management(filePath, projectedGeoTiff, arcpy.SpatialReference(3857))
             fileList[file].append(projectedGeoTiff + ".tif")
             
counter = 1
for file in fileList.keys():
    mosiacImage = "testMosiac" + str(counter)
    bandsArray = calculateBandsArray(fileList[file])
    print(bandsArray)
    if not (arcpy.Exists(mosiacImage)):
        arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
                                       "16_BIT_SIGNED","#","1", "MEAN","MATCH")
    print('FINISHED with September ' + str(counter))
    counter = counter + 1

