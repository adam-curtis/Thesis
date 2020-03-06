devtools::install_github("MatMatt/MODIS", ref = "develop")
library(MODIS)
library(reticulate)

year = 2000

#Sets up environment paths for downloading the HDF and creating geoTiff data, along with the location of my GDAL
localPath = "C:\\Thesis"
outPath = "C:\\Thesis"
GdalPath = "C:\\OSGeo4W64\\bin"
TifFolder = paste("USAgeoTiff",year,sep="")
MODISoptions(gdalPath = GdalPath, localArcPath = localPath, outDirPath = outPath)

#Vector of tiles for the continental US for a Sinusodial grid
vectorTileH <- c(8,9,10,11,12,13,8,9,10,11,12,10)
vectorTileV <- c(4,4,4,4,4,4,5,5,5,5,5,6)
vLength <- length(vectorTileV)

#Calls HTTP Request to NASA's Data Archive and downloads all of the MCD19A2 data for the given time period
getHdf(product = "MCD19A2", begin = paste(year,02,26,sep="."), end = paste(year,12,31,sep="."),
       tileH = 8:13, tileV = 4:6)

for(i in 1:vLength) {
  output_dir <- file.path(TifFolder, paste("\\H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep=""))
  if (!dir.exists(output_dir)){
    dir.create(output_dir)
  }
}
#Runs GDAL function on local HDF data to process the files into geoTIFF images with the extracted Optical_Depth_47 band       
for(i in 1:vLength) {
    runGdal("MCD19A2"
            , begin = paste(year,01,01,sep="."), end = paste(year,12,31,sep=".")
            , tileH = vectorTileH[i],tileV = vectorTileV[i]
            , job = paste(TifFolder,"\\H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
            , SDSstring = "1000000000000", localArcPath=outPath)
}






#use_python("C:\\Users\\acurt\\AppData\\Local\\ESRI\\conda\\envs\\arcgispro-py3-clone\\python.exe")
#source_python("C:\\Thesis\\PythonScripts\\calculatePM2_5Model.py")
#model <- calculateModel(paste(outPath,"\\",TifFolder, sep=""), year)
#model
