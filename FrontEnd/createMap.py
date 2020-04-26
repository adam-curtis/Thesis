
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
projectName = sys.argv[2]
date = sys.argv[3]
sys.stdout.write(projectFilePath + '\n')
sys.stdout.write(projectName + '\n')
sys.stdout.write(date + '\n')
tifFiles = projectFilePath + '\\TIFS'
projDB = projectName +".gdb"
projectedGeoTiffDB =projectFilePath + "\\" + projDB
frontEndPath = projectFilePath[:projectFilePath.rfind("/")]
copyAprx = arcpy.mp.ArcGISProject(frontEndPath + r"\CopyProject\CopyProject.aprx")
copyAprx.saveACopy(projectFilePath+"\\"+projectName+".aprx")
aprx = arcpy.mp.ArcGISProject(projectFilePath+"\\"+projectName+".aprx")

#Creates File Geodatabase for the reprojected geoTiffs
if not arcpy.Exists(projectedGeoTiffDB):
    arcpy.CreateFileGDB_management(projectFilePath,projDB)
print(projectedGeoTiffDB)
arcpy.env.workspace = projectedGeoTiffDB
aprx.defaultGeodatabase = projectedGeoTiffDB

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
projectMap = aprx.listMaps()[0]
print(fileList)
for file in fileList.keys():
    mosiacImage = "satelliteMosiac" + str(counter)
    rasterImage = "particulateMatter" + str(counter)
    bandsArray = calculateBandsArray(fileList[file])
    print(bandsArray)
    if not (arcpy.Exists(mosiacImage)):
        arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
                                       "16_BIT_SIGNED","#","1", "MEAN","MATCH")
    expression = "Int(27.89284+0.06231*\""+mosiacImage+"\")"
    if not (arcpy.Exists(rasterImage)):
        arcpy.gp.RasterCalculator_sa(expression, rasterImage)
   
    rasterPath = projectedGeoTiffDB + "\\" + rasterImage
    symbologyCopyPath = frontEndPath + r"\CopyProject\copySymbology.lyrx"
    polygonLayerName = "ParticulateMatter"
    plName = "ParticulateMatter2_5"
    #result = arcpy.MakeRasterLayer_management(rasterPath, rasterName,"SIMPLIFY","VALUE")
    #layer = result.getOutput(0)
    result2 = arcpy.RasterToPolygon_conversion(rasterImage,polygonLayerName)
    featureLayer = arcpy.MakeFeatureLayer_management(result2[0],plName)
    arcpy.ApplySymbologyFromLayer_management(featureLayer[0],symbologyCopyPath)
    projectMap.addLayer(featureLayer[0])
    lyr = projectMap.listLayers(plName)[0]
    # sym = lyr.symbology
    # breakLabels = ['≤ 50 - Good', '≤ 100 - Moderate', '≤ 150 - Unhealthy for sensitive groups','≤ 200 - Unhealthy', '≤ 300 - Very Unhealthy', '≤ 565 - Hazardous']
    # breakValues = [50,100,150,200,300,565]
    # colorHues = [100,60,40,0,278,331]
    # colorSats = [100,100,100,100,50.36,50.36]
    # colorVals = [65.88,96,100,90.2,53.73,53.73]
    # classCounter = 0
    # sym.renderer.breakCount = 6
    # for brk in sym.renderer.classBreaks:
    #     brk.upperBound = breakValues[classCounter]
    #     brk.label = breakLabels[classCounter]
    #     brk.symbol.color = {'HSV' : [colorHues[classCounter], colorSats[classCounter], colorVals[classCounter],100]}
    #     classCounter += 1
    
    # lyr.symbology = sym
    counter = counter + 1
    
aprx.save()

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

print("ArcGISOnline ID: ",result[3])
print("Successfully Uploaded service.")
sys.stdout.write(result[3])
del aprx