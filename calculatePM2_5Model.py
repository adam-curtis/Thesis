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

def calculateModel(hdfFiles, year):
    aprx = arcpy.mp.ArcGISProject(r'C:\Thesis\PM2018\PM2018.aprx')
    arcpy.env.overwriteOutput = True
    
    #Ground Monitor Data & Variables
    dailyCSV = r'C:\Thesis\daily'+str(year)+'.csv'
    xYLayer = 'dailypm'+str(year)
    savedLayer = r'C:\Thesis\PM2018\PM2018\PM'+str(year)+'layer'
    featureClass=r'C:\Thesis\PM2018\PM'+str(year)+'.gdb\\pm'+str(year)+'data'
    queriedFeatureClass=r'C:\Thesis\PM2018\PM'+str(year)+'.gdb\\queriedPM'+str(year)
    projDB = "proj"+str(year)+"Tiff.gdb"
    projectedGeoTiffDB ='C:\\Thesis\\' + projDB
    pmDB = r'C:\Thesis\PM2018\PM'+str(year)+'.gdb'
    if not arcpy.Exists(pmDB):
            arcpy.CreateFileGDB_management("C:\\Thesis\\PM2018", "PM"+str(year)+'.gdb')
    arcpy.env.workspace = pmDB
    
    try:
        if os.path.exists(savedLayer+".lyrx"):
            os.remove(savedLayer+".lyrx")
     
        arcpy.MakeXYEventLayer_management(dailyCSV, 'longitude', 'latitude', xYLayer, arcpy.SpatialReference(4326))
        print("Made Event Layer")
        arcpy.SaveToLayerFile_management(xYLayer, savedLayer)
        print("Saved to Layer File")
        arcpy.CopyFeatures_management(savedLayer+".lyrx", featureClass)
        arcpy.AddField_management(featureClass, "AverageAOD", "FLOAT",field_is_nullable="NULLABLE")
        qFC = arcpy.SelectLayerByAttribute_management(featureClass, "NEW_SELECTION", '"Sample_Duration" <> ' + "'1 HOUR'")
        arcpy.CopyFeatures_management(qFC, queriedFeatureClass)
        arcpy.DeleteIdentical_management(queriedFeatureClass, ["Latitude", "Longitude", "Date_Local"])
        print("Removed all 1 Hour sample durations and filtered out identical values")
  
        start_date = date(year, 2, 26)
        end_date = date(year, 12, 31)
        startCounterDate = datetime.datetime(year, 2, 26)
        counter = int(startCounterDate.strftime("%j"))
        delta = timedelta(days=1) 
        while start_date <= end_date:
            dateStr = start_date.strftime("%Y-%m-%d")
            currentDayFC = featureClass + str(counter)
            if not arcpy.Exists(currentDayFC):
                qFC = arcpy.SelectLayerByAttribute_management(queriedFeatureClass, "NEW_SELECTION",  '"Date_Local" = timestamp \'' + dateStr + '\'')
                arcpy.CopyFeatures_management(qFC, currentDayFC)
            start_date += delta
            counter = counter + 1

        print('finished creating all queried feature points')
        

        arcpy.env.workspace = projectedGeoTiffDB
        fileList = dict()

        for subdir, dirs, files in os.walk(hdfFiles):
            for file in files:
                if file.endswith(".tif"):
                    fileList[file] = []

        #Creates File Geodatabase for the reprojected geoTiffs
        if not arcpy.Exists('C:\\Thesis\\'+projDB):
            arcpy.CreateFileGDB_management("C:\\Thesis", projDB)

        #Reprojects the geoTIFFs created in R to work with Mercator and the ground monitor data, and then adds the file path of the specified
        #fileList since there are twelve separate geoTIFFs for a given day
        for subdir, dirs, files in os.walk(hdfFiles):
            for file in files:
                if file.endswith(".tif"):
                    currTile = subdir.split("\\")[-1]
                    fileID = file[9:16]
                    filePath = subdir + "\\" + file
                    projectedGeoTiff = projectedGeoTiffDB + "\\" + currTile + "_" + fileID
                    if not arcpy.Exists(projectedGeoTiff):
                        arcpy.ProjectRaster_management(filePath, projectedGeoTiff, arcpy.SpatialReference(3857))
                    fileList[file].append(projectedGeoTiff + ".tif")
        
        print('Projected tiffs finished')
        arcpy.env.workspace = pmDB
    
        for file in fileList.keys():
            dayOfYear = int(file[13:16])
            currentDayFC = featureClass + str(dayOfYear)

            #For each valid geoTiff image, it calculates the intersection values with the ground monitor data for each band
            for tif in fileList[file]:
                arcpy.sa.ExtractMultiValuesToPoints(currentDayFC, tif, "BILINEAR")

            #Calls calculateFieldsArray to locate all of the tile geotiffs for a specific date (there are 12 separate tile images for the continental US)
            #And then locates all of the separate band fields calculated in ExtractMultiValuesToPoints to create an AverageAOD for non-null values
            fieldsArray = calculateFieldsArray(fileList[file])
            calculateAverage = "averageFields("+str(fieldsArray)+")"
            arcpy.CalculateField_management(currentDayFC, "AverageAOD", calculateAverage,"PYTHON3") 

            #Checks if there are 5 or AverageAOD values that are not null. The linear regression tool will fail if there are not enough values
            #For some periods of time, especially in year 2000, there were days where no data was shown
            testFC = arcpy.SelectLayerByAttribute_management(currentDayFC, "NEW_SELECTION", "AverageAOD IS NOT NULL")
            validCount = arcpy.GetCount_management(testFC)
            validCount = int(validCount.getOutput(0))
            if validCount >= 5:
                arcpy.stats.GeneralizedLinearRegression(currentDayFC, "AQI", "CONTINUOUS",
                                                        "LinearRegression"+str(dayOfYear), "AverageAOD")
        
        print('Finished Multi Value & Linear Regression')
        #Creates arrays for all of the seasons and adds the correct LinearRegression feature points to the correct array for seasonal correlation
        linearR = "LinearRegression"
        
        fullYearArray = []
        winterEnd = datetime.datetime(year, 3, 20)
        winterEndDay = int(winterEnd.strftime("%j"))
        winterArray = []
        
        springEnd = datetime.datetime(year,6,20)
        springEndDay = int(springEnd.strftime("%j"))
        springArray = []
        
        summerEnd = datetime.datetime(year,9,22)
        summerEndDay = int(summerEnd.strftime("%j"))
        summerArray = []
        
        fallEnd = datetime.datetime(year,12,21)
        fallEndDay = int(fallEnd.strftime("%j"))
        fallArray = []
        
        for i in range(1,366):
            if arcpy.Exists(linearR+str(i)):
                fullYearArray.append(linearR+str(i))
                if (i < winterEndDay or i > fallEndDay):
                    winterArray.append(linearR + str(i))
                elif (i < springEndDay):
                    springArray.append(linearR + str(i))
                elif (i < summerEndDay):
                    summerArray.append(linearR + str(i))
                else:
                    fallArray.append(linearR + str(i))
                
        
        arcpy.Merge_management(winterArray, 'LinearRegression' + str(year)+'Winter')
        arcpy.Merge_management(springArray, 'LinearRegression' + str(year)+'Spring')
        arcpy.Merge_management(summerArray, 'LinearRegression' + str(year)+'Summer')
        arcpy.Merge_management(fallArray, 'LinearRegression' + str(year)+'Fall')
        arcpy.Merge_management(fullYearArray, 'LinearRegressionFull' + str(year))

        # mosiacImage = "mosiac"+str(year)+str(225)
        # file = "MCD19A2.A2018225.Optical_Depth_047.tif"
        # if arcpy.Exists(mosiacImage):
        #     arcpy.Delete_management(mosiacImage)
        # arcpy.env.workspace = projectedGeoTiffDB
        # bandsArray = calculateBandsArray(fileList[file])
        # arcpy.MosaicToNewRaster_management(bandsArray,projectedGeoTiffDB,mosiacImage, arcpy.SpatialReference(3857),
        #                                     "16_BIT_SIGNED","#","1", "MEAN","MATCH")
    except:
        print(arcpy.GetMessages())
    aprx.save()

start_time = time.time()
calculateModel(r'C:\\Thesis\\USAgeoTiff2000', 2000)
print("--- %s seconds ---" % (time.time() - start_time))