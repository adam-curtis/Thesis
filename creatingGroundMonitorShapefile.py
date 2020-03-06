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
import datetime

def calculateModel(hdfFiles) :
    # Local Variables
    dailycsv2018 = r'C:\Thesis\daily2018.csv'
    groundMonitorData = 'dailypm2018'
    x_coords = 'longitude'
    y_coords = 'latitude'
    spRef = arcpy.SpatialReference(4326)
    aprx = arcpy.mp.ArcGISProject(r'C:\Thesis\PM2018\PM2018.aprx')
    arcpy.env.workspace = "C:/data"
    savedLayer = r'C:\Thesis\PM2018\PM2018.gdb\PM2018'
    featureClass=r'C:\Thesis\PM2018\PM2018.gdb\pm2018data'
    if os.path.exists(savedLayer+".lyrx"):
        os.remove(savedLayer+".lyrx")
    if arcpy.Exists(featureClass):
        arcpy.Delete_management(featureClass)
    
    arcpy.MakeXYEventLayer_management(dailycsv2018, x_coords, y_coords, groundMonitorData, spRef)
    arcpy.SaveToLayerFile_management(groundMonitorData, savedLayer)
    arcpy.CopyFeatures_management(r'C:\Thesis\PM2018\PM2018.gdb\PM2018.lyrx', featureClass)
    aprxMap = aprx.listMaps()[0]    
    aprxMap.addDataFromPath(featureClass)
    arcpy.SelectLayerByAttribute_management(featureClass, "NEW_SELECTION", "[Sample Duration] = '1 HOUR'")
#     arcpy.DeleteRows(lyr)
#     arcpy.DeleteIdentical_management(lyr, [Latitude", "Longitude", "Date Local"])
#     
#     arcpy.AddField_management(lyr, "AverageAOD", "FLOAT",field_is_nullable="NULLABLE")
# 
#     for subdir, dirs, files in os.walk(hdfFiles):
#         for file in files:
#            if file.endswith(".tif"):
#                dayOfYear = int(file[13:16])
#                year = int(file[9:13])
#                theDate = datetime.datetime(year, 1, 1) + datetime.timedelta(dayOfYear - 1)
#                lyr.definitionQuery = '"Date Local" = timestamp \'' + str(theDate) + '\''
#                break;
    aprx.save()
# =============================================================================

    return hdfFiles;

calculateModel(r'C:\Thesis\USAMODIS')