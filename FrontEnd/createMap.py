
import sys
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


def createFileList(tifFiles):
    tempFileList = dict()     
    for subdir, dirs, files in os.walk(tifFiles):
        for file in files:
            if file.endswith(".tif"):
                tempFileList[file] = []
    return tempFileList
    
#Setup Environment, grab the project path from the passed system argument and grab the project name
projectFilePath = sys.argv[1]
projectName = sys.argv[2]
date = sys.argv[3]
tifFiles = projectFilePath + '\\TIFS'
projDB = projectName +".gdb"
projectedGeoTiffDB =projectFilePath + "\\" + projDB
frontEndPath = projectFilePath[:projectFilePath.rfind("/")]

#Copy default project -- ArcGIS does not allow you to create a project from scratch, so I needed to have a blank default one to automate new projects
copyAprx = arcpy.mp.ArcGISProject(frontEndPath + r"\CopyProject\CopyProject.aprx")
copyAprx.saveACopy(projectFilePath+"\\"+projectName+".aprx")
aprx = arcpy.mp.ArcGISProject(projectFilePath+"\\"+projectName+".aprx")

#Creates File Geodatabase for the reprojected geoTiffs
if not arcpy.Exists(projectedGeoTiffDB):
    arcpy.CreateFileGDB_management(projectFilePath,projDB)
arcpy.env.workspace = projectedGeoTiffDB
aprx.defaultGeodatabase = projectedGeoTiffDB

#Since all geoTIFFs for a specific day are named the same, the tiles need to be extracted from the separate TIF folders and put into separate values in an array
fileList = createFileList(tifFiles)  
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
projectMap = aprx.listMaps()[0]

#Creates a mosiac image from the passed in geoTIFF images and then calculates a new raster showing the estimated particulate matter using my model
for file in fileList.keys():
    mosiacImage = "satelliteMosiac" + str(counter)
    rasterImage = "particulateMatter" + str(counter)

    #Finds all bands within the geoTIFFs, and finds the average pixel value across the specified area if there is any overlap, then uses the
    #Raster Calculator to calculate the estimate particulate matter value
    bandsArray = calculateBandsArray(fileList[file])
    if not (arcpy.Exists(mosiacImage)):
        arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
                                       "16_BIT_SIGNED","#","1", "MEAN","MATCH")
    expression = "Int(27.89284+0.06231*\""+mosiacImage+"\")"
    if not (arcpy.Exists(rasterImage)):
        arcpy.gp.RasterCalculator_sa(expression, rasterImage)
    
    rasterPath = projectedGeoTiffDB + "\\" + rasterImage
    symbologyCopyPath = frontEndPath + r"\CopyProject\ParticulateMatterTest.lyrx"
    polygonLayerName = "ParticulateMatter"
    plName = "ParticulateMatter2_5"

    #Uses the symbology from a layer within the copied project, used to show consistent symbology for all automated projects
    #Converted raster to a polygon layer because rasters were producing errors and not showing during the upload process
    result2 = arcpy.RasterToPolygon_conversion(rasterImage,polygonLayerName)
    featureLayer = arcpy.MakeFeatureLayer_management(result2[0],plName)
    arcpy.ApplySymbologyFromLayer_management(featureLayer[0],symbologyCopyPath)
    projectMap.addLayer(featureLayer[0])
    lyr = projectMap.listLayers(plName)[0]
    counter = counter + 1
    
aprx.save()

#Setup project paths and layers to be used in ArcGIS Online uploading process
service = projectName
sddraft_output_filename = projectFilePath+"\\"+service+".sddraft"
sd_output_filename = projectFilePath+"\\"+service+".sd"
lyrs = []
lyrs.append(projectMap.listLayers()[0])

# Create TileSharingDraft and set service properties
sharing_draft = projectMap.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service, lyrs)
print(arcpy.GetMessages())
sharing_draft.summary = "My Summary"
sharing_draft.tags = "My Tags"
sharing_draft.description = "My Description"

# Create Service Definition Draft file
sharing_draft.exportToSDDraft(sddraft_output_filename)
print(arcpy.GetMessages())

# Stage Service
print(sddraft_output_filename, sd_output_filename)
arcpy.StageService_server(sddraft_output_filename, sd_output_filename)
print(arcpy.GetMessages())

# Share to portal
print("Uploading Service Definition...")
result = arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services",in_override="OVERRIDE_DEFINITION", in_public="PUBLIC")
print(arcpy.GetMessages())

#Print portal item id and return that id to the R Script to be passed to the JavaScript File
print("ArcGISOnline ID: ",result[3])
print("Successfully Uploaded service.")
sys.stdout.write(result[3])
del aprx