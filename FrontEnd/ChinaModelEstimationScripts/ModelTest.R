#.libPaths("C:/Users/acurt/R")
#install.packages("fs")
#devtools::install_github("MatMatt/MODIS", ref = "develop")
library(MODIS)
library(reticulate)

#Sets up environment paths for downloading the HDF and creating geoTiff data, along with the location of my GDAL
localPath = "C:\\Thesis"
year = 2016
outPath = "C:\\Thesis"
GdalPath = "C:\\OSGeo4W64\\bin"
TifFolder = paste("USAgeoTiff",year,sep="")
MODISoptions(gdalPath = GdalPath, localArcPath = localPath, outDirPath = outPath)
getTile()
vectorTileH <- c(21,22,22,23,23,23,24,24,24,24,25,25,25,25,26,26,26,26,27,27,27,28,28,28,28,29,29,30)
vectorTileV <- c(3,3,4,3,4,5,3,4,5,6,3,4,5,6,3,4,5,6,4,5,6,4,5,6,7,5)
vLength <- length(vectorTileV)

for(i in 1:vLength) {
  output_dir <- file.path("C:\\Thesis\\ChinaModelTest", paste("\\H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep=""))
  if (!dir.exists(output_dir)){
    dir.create(output_dir)
  } else {
    print("Dir already exists!")
  }
}
for(i in 1:vLength) {
  runGdal("MCD19A2"
          , begin = "2019-11-01", end = "2019-11-10"
          , tileH = vectorTileH[i],tileV = vectorTileV[i]
          , job = paste("ChinaModelTest","\\H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
          , SDSstring = "1000000000000", localArcPath=outPath)
}