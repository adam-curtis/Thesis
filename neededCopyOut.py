#-------------------------------------------------------------------------------
# Name:        calculatePM2_5Model
# Purpose:
#
# Author:      acurt
#
# Created:     16/09/2019
# Copyright:   (c) acurt 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import os
from datetime import date, timedelta
from pathlib import Path
import time

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

def calculateModel(hdfFiles, year):
    # GIS Project Variables
    
    aprx = arcpy.mp.ArcGISProject(r'C:\Thesis\PM2018\PM2018.aprx')
    arcpy.env.overwriteOutput = True
    
    #Ground Monitor Data & Variables
    dailyCSV = r'C:\Thesis\daily2018.csv'
    xYLayer = 'dailypm'+str(year)
    savedLayer = r'C:\Thesis\PM2018\PM2018\PM2018layer'
    featureClass=r'C:\Thesis\PM2018\PM2018.gdb\pm2018data'
    queriedFeatureClass=r'C:\Thesis\PM2018\PM2018.gdb\queriedPM2018'
    projDB = "proj"+str(year)+"Tiff.gdb"
    projectedGeoTiffDB ='C:\\Thesis\\' + projDB
    arcpy.env.workspace = r'C:\Thesis\PM2018\PM2018.gdb'
    
    try:
        # if os.path.exists(savedLayer+".lyrx"):
        #     os.remove(savedLayer+".lyrx")
     
        # arcpy.MakeXYEventLayer_management(dailyCSV, 'longitude', 'latitude', xYLayer, arcpy.SpatialReference(4326))
        # print("Made Event Layer")
        # arcpy.SaveToLayerFile_management(xYLayer, savedLayer)
        # print("Saved to Layer File")
        # arcpy.CopyFeatures_management(savedLayer+".lyrx", featureClass)
        # arcpy.AddField_management(featureClass, "AverageAOD", "FLOAT",field_is_nullable="NULLABLE")
        # qFC = arcpy.SelectLayerByAttribute_management(featureClass, "NEW_SELECTION", '"Sample_Duration" <> ' + "'1 HOUR'")
        # arcpy.CopyFeatures_management(qFC, queriedFeatureClass)
        # arcpy.DeleteIdentical_management(queriedFeatureClass, ["Latitude", "Longitude", "Date_Local"])
        # print("Removed all 1 Hour sample durations and filtered out identical values")
  
        # start_date = date(year, 1, 1)
        # end_date = date(year, 12, 31)
        # counter = 1
        # delta = timedelta(days=1) 
        # while start_date <= end_date:
        #     dateStr = start_date.strftime("%Y-%m-%d")
        #     currentDayFC = featureClass + str(counter)
        #     if not arcpy.Exists(currentDayFC):
        #         qFC = arcpy.SelectLayerByAttribute_management(queriedFeatureClass, "NEW_SELECTION",  '"Date_Local" = timestamp \'' + dateStr + '\'')
        #         arcpy.CopyFeatures_management(qFC, currentDayFC)
        #     start_date += delta
        #     counter = counter + 1

        # print('finished creating all queried feature points')
        
        # arcpy.env.workspace = projectedGeoTiffDB
        # fileList = dict()

        # for filename in os.listdir(hdfFiles+"\\H8V4"):
        #     fileList[filename] = []
        
        # if not arcpy.Exists('C:\\Thesis\\'+projDB):
        #     arcpy.CreateFileGDB_management("C:\\Thesis", projDB)
            
        # for subdir, dirs, files in os.walk(hdfFiles):
        #     for file in files:
        #         if file.endswith(".tif"):
        #             currTile = subdir.split("\\")[-1]
        #             fileID = file[9:16]
        #             filePath = subdir + "\\" + file
        #             projectedGeoTiff = projectedGeoTiffDB + "\\" + currTile + "_" + fileID
        #             if not arcpy.Exists(currTile+"_"+fileID):
        #                 arcpy.ProjectRaster_management(filePath, projectedGeoTiff, arcpy.SpatialReference(3857))
        #             fileList[file].append(projectedGeoTiff + ".tif")
        
        # print('Projected tiffs finished')
        arcpy.env.workspace = r'C:\Thesis\PM2018\PM2018.gdb'
        
        # for file in fileList.keys():
        #     dayOfYear = int(file[13:16])
        #     currentDayFC = featureClass + str(dayOfYear)
        #     for tif in fileList[file]:
        #         arcpy.sa.ExtractMultiValuesToPoints(currentDayFC, tif, "BILINEAR")
        #     fieldsArray = calculateFieldsArray(fileList[file])
        #     calculateAverage = "averageFields("+str(fieldsArray)+")"
        #     arcpy.CalculateField_management(currentDayFC, "AverageAOD", calculateAverage,"PYTHON3"); 
        #     arcpy.stats.GeneralizedLinearRegression(currentDayFC, "AQI", "CONTINUOUS",
        #                                             "LinearRegression"+str(dayOfYear), "AverageAOD")
        #     print(currentDayFC)

        linearR = "LinearRegression"
        
        fullYearArray = []
        winterEnd = datetime.datetime(year, 3, 20)
        winterEndDay = int(winterEnd.strftime("%j"))
        winterArray = []
        print(winterEndDay)
        
        springEnd = datetime.datetime(year,6,20)
        springEndDay = int(springEnd.strftime("%j"))
        springArray = []
        print(springEndDay)
        
        summerEnd = datetime.datetime(year,9,22)
        summerEndDay = int(summerEnd.strftime("%j"))
        summerArray = []
        print(summerEndDay)
        
        fallEnd = datetime.datetime(year,12,21)
        fallEndDay = int(fallEnd.strftime("%j"))
        fallArray = []
        print(fallEndDay)
        

        for i in range(1,366):
            fullYearArray.append(linearR+str(i))
            if (i < winterEndDay or i > fallEndDay):
                winterArray.append(linearR + str(i))
            elif (i < springEndDay):
                springArray.append(linearR + str(i))
            elif (i < summerEndDay):
                summerArray.append(linearR + str(i))
            else:
                fallArray.append(linearR + str(i))
        
        # arcpy.Merge_management(winterArray, 'LinearRegression2018Winter')
        # arcpy.Merge_management(springArray, 'LinearRegression2018Spring')
        # arcpy.Merge_management(summerArray, 'LinearRegression2018Summer')
        # arcpy.Merge_management(fallArray, 'LinearRegression2018Fall')
        # arcpy.Merge_management(fullYearArray, 'LinearRegressionFull2018')

        mosiacImage = "mosiac"+str(year)+str(1)
        arcpy.env.workspace = projectedGeoTiffDB
        bandsArray = calculateBandsArray(fileList[hdfFiles+"\\H8V4"+"\\MCD19A2.A2018001.Optical_Depth_047.tif"])
        arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
                                            "16_BIT_UNSIGNED","#","1", "MEAN","MATCH")  
    except:
        print(arcpy.GetMessages())
    aprx.save()

start_time = time.time()
calculateModel(r'C:\Thesis\USAgeoTiff2018', 2018)
print("--- %s seconds ---" % (time.time() - start_time))