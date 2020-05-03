#update.packages(repos = "http://cran.us.r-project.org")
if (!require(MODIS)) install.packages("MODIS", repos = "http://cran.us.r-project.org"); library(MODIS)
if (!require(here)) devtools::install_github("krlmlr/here"); library(here)
if (!require(stringr)) install.packages("stringr", repos = "http://cran.us.r-project.org"); library(stringr)
if (!require(reticulate)) install.packages("reticulate", repos = "http://cran.us.r-project.org"); library(reticulate)

#Retrieves the arguments for the project name and date, converts the date to the correct syntax, and manages the setup for the MODIS library
GdalPath = "C:\\OSGeo4W64\\bin"
args <- commandArgs(trailingOnly=TRUE)
projectName <- args[1]
date <- args[2]
dateSplit <- strsplit(date,"-")
date <- paste(dateSplit[[1]][3],"-",dateSplit[[1]][1],"-",dateSplit[[1]][2],sep="")
projectFilePath <- paste(here(),"FrontEnd/Projects",projectName,sep="/")
tifFilePath <- paste(projectFilePath,"TIFs",sep="/")

if (!dir.exists(projectFilePath)){
    dir.create(projectFilePath)
} else {
   print("-1");
   quit(status=1);
}
if (!dir.exists(tifFilePath)){
    dir.create(tifFilePath)
}

#This function from the MODIS library allows the user to have an interactive display for picking their desired satellite imagery tiles
#I originally hoped to use their country database, but it was too unreliable and was unable to show results for many countries
tiles <- getTile()
tiles <- tiles@tile
tiles <- unique(tiles)

vectorTileH <- vector()
vectorTileV <- vector()
vLength <- length(tiles)

for(i in 1:vLength) 
{
  test <- strsplit(tiles[i],"v")
  test[[1]][1] <- sub('h', '', test[[1]][1])
  h <- test[[1]][1]
  v <- test[[1]][2]
  vectorTileH <- c(vectorTileH,h)
  vectorTileV <- c(vectorTileV,v)
}
localPath = paste(here(),"FrontEnd",sep="/")
MODISoptions(gdalPath = GdalPath, localArcPath = localPath, outDirPath = projectFilePath)
for(i in 1:vLength) {
  output_dir <- paste(projectFilePath,"/TIFs/H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
  if (!dir.exists(output_dir)){
    dir.create(output_dir)
  } 
  getHdf(product = "MCD19A2", begin = date, end = date,
       tileH = vectorTileH[i],tileV = vectorTileV[i],outDirPath=projectFilePath)
}
for(i in 1:vLength) {
  output_dir <- paste(here(),"/FrontEnd/Projects/",projectName,"/TIFs/H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
  runGdal("MCD19A2"
          , begin = date, end = date
          , tileH = vectorTileH[i],tileV = vectorTileV[i]
          , job = paste("TIFs","/H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
          , SDSstring = "1000000000000",localArcPath=output_dir,forceDownload=TRUE)
}

projectName <- paste("\"",projectName,"\"",sep="")
system_call <-paste("python createMap.py",projectFilePath,projectName,date)
python_response <- system(system_call, intern=TRUE)
print("Finished")
print(python_response)