#update.packages(repos = "http://cran.us.r-project.org")

if (!require(MODIS)) install.packages("MODIS", repos = "http://cran.us.r-project.org"); library(MODIS)
if (!require(here)) devtools::install_github("krlmlr/here"); library(here)
if (!require(stringr)) install.packages("stringr", repos = "http://cran.us.r-project.org"); library(stringr)
if (!require(reticulate)) install.packages("reticulate", repos = "http://cran.us.r-project.org"); library(reticulate)
#if (!require(tidyverse)) install.packages("tidyverse", repos = "http://cran.us.r-project.org"); library(tidyverse)
GdalPath = "C:\\OSGeo4W64\\bin"
args <- commandArgs(trailingOnly=TRUE)
country <- args[1]
date <- args[2]
date <- str_replace_all(date,"/","-")
dateSplit <- strsplit(date,"-")
date <- paste(dateSplit[[1]][3],"-",dateSplit[[1]][1],"-",dateSplit[[1]][2],sep="")
country_date <- paste(country,date)
country_date <- str_replace_all(country_date," ","_")
projectFilePath <- paste(here(),"FrontEnd",country_date,sep="/")
tifFilePath <- paste(projectFilePath,"TIFs",sep="/")
if (dir.exists(projectFilePath)){
    print("exists")
   #unlink(projectFilePath, recursive=TRUE)
}
dir.create(projectFilePath)

if (!dir.exists(tifFilePath)){
    dir.create(tifFilePath)
}
tiles <- getTile()
tiles <- tiles@tile
tiles <- unique(tiles)
print(tiles)
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
  print(output_dir)
  if (!dir.exists(output_dir)){
    dir.create(output_dir)
  } else {
    print("Dir already exists!")
  }
  getHdf(product = "MCD19A2", begin = date, end = date,
       tileH = vectorTileH[i],tileV = vectorTileV[i],outDirPath=projectFilePath)
}
for(i in 1:vLength) {
  output_dir <- paste(here(),"/FrontEnd/",country_date,"/TIFs/H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
  runGdal("MCD19A2"
          , begin = date, end = date
          , tileH = vectorTileH[i],tileV = vectorTileV[i]
          , job = paste("TIFs","/H",toString(vectorTileH[i]),"V",toString(vectorTileV[i]),sep="")
          , SDSstring = "1000000000000",localArcPath=output_dir,forceDownload=TRUE)
}
print(date)
country <- paste("\"",country,"\"",sep="")

system_call <-paste("python createMap.py",projectFilePath,country,date)
#print(system_call)
system(system_call)
print("Finished")
