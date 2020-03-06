#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      acurt
#
# Created:     16/09/2019
# Copyright:   (c) acurt 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import os
import csv

hourly2018 = r"C:\Users\acurt\Thesis\hourly2018.csv"
arcpy.env.workspace = r"C:\Users\acurt\Thesis\DB.gdb"
# Set the local variables

x_coords = "longitude"
y_coords = "latitude"
spRef = r"Coordinate Systems\Geographic Coordinate Systems\North America\USA and territories\NAD 1983 (2011).prj"

csvSplit = open(hourly2018, 'r').readlines()
file = 1
for j in range(len(csvSplit)):
    if j % 500000 == 0:
        linesArray = csvSplit[j:j+500000]
        if j != 0:
            linesArray.insert(0, csvSplit[0]);
        open(str(hourly2018)+ str(file) + '.csv', 'w+').writelines(linesArray);
        in_table = r"C:\Users\acurt\Thesis\hourly2018" + '.csv' + str(file) + '.csv';
        outLocation = r"C:\Users\acurt\Thesis\HourlyData";
        feature = arcpy.MakeXYEventLayer_management(in_table, x_coords, y_coords, "hourly" + str(file), spRef);
        arcpy.FeatureClassToShapefile_conversion([feature],outLocation);
        file += 1;