import arcpy
import os
from pathlib import Path

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


tifFiles = 'C:\\Thesis\\ChinaModelTest'
projDB = "projResults.gdb"
projectedGeoTiffDB ='C:\\Thesis\\' + projDB

#Creates File Geodatabase for the reprojected geoTiffs
if not arcpy.Exists('C:\\Thesis\\'+projDB):
    arcpy.CreateFileGDB_management("C:\\Thesis", projDB)

arcpy.env.workspace = "C:\\Thesis\\" + projDB
 
#Reprojects the geoTIFFs created in R to work with Mercator and the ground monitor data, and then adds the file path of the specified
         #fileList since there are twelve separate geoTIFFs for a given day
fileList = dict()        
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
    mosiacImage = "mosiac2019November" + str(counter)
    bandsArray = calculateBandsArray(fileList[file])
    print(bandsArray)
    if not (arcpy.Exists(mosiacImage)):
        arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
                                       "16_BIT_SIGNED","#","1", "MEAN","MATCH")
    print('FINISHED with September ' + str(counter))
    counter = counter + 1