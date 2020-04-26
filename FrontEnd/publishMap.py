import sys
import arcpy
import os
from pathlib import Path
import arcgis

aprx = arcpy.mp.ArcGISProject("C:\\Thesis\\Scripts\\FrontEnd\\Projects\\Azerbaijan_2010-04-13\\Azerbaijan.aprx")
sddraft_output_filename = r"C:\Thesis\Scripts\FrontEnd\Projects\Azerbaijan_2010-04-13\Attempt6.sddraft"
sd_output_filename = r"C:\Thesis\Scripts\FrontEnd\Projects\Azerbaijan_2010-04-13\Attempt6.sd"
m = aprx.listMaps()[0]

# arcpy.mp.CreateWebLayerSDDraft(m,sddraft_output_filename,'Attempt6','MY_HOSTED_SERVICES')
# print(arcpy.GetMessages())
# arcpy.StageService_server(sddraft_output_filename, sd_output_filename)
# print(arcpy.GetMessages())
# arcpy.UploadServiceDefinition_server(sd_output_filename, 'My Hosted Services')
# print(arcpy.GetMessages())

# Set output file names
outdir = r"C:\Thesis\Scripts\FrontEnd\Projects\Azerbaijan_2010-04-13"
service = "TestAgain2"
sddraft_output_filename = r"C:\Thesis\Scripts\FrontEnd\Projects\Azerbaijan_2010-04-13\TestAgain2.sddraft"
sd_output_filename = r"C:\Thesis\Scripts\FrontEnd\Projects\Azerbaijan_2010-04-13\TestAgain2.sd"
lyrs = []
lyrs.append(m.listLayers()[0])
lyrs.append(m.listLayers()[1])

# Create TileSharingDraft and set service properties
sharing_draft = m.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service, lyrs)
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
result = arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services")
print(arcpy.GetMessages())

print("ArcGISOnline ID: ",result[3])
#sys.stdout.write(result[3])
print("Successfully Uploaded service.")