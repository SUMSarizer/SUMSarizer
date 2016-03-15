#
# Usage: Rscript ml_script.R ../data/studydata.csv ../data/userlabels.csv ../data/studydata_ml.csv
#
# Note: should be invoked from the `ml_labeler` directory
#

library(plyr)
library(origami)
source("features.R")

args = commandArgs(trailingOnly=TRUE)

studydatafile=args[1] # e.g. studydata.csv
userlabelfile=args[2] # e.g. userlabels.csv
outputfile=args[3]


#INPUT DATA
#generated from querydump.sql
studydata=read.csv(studydatafile) #the sensor readings
userlabels=read.csv(userlabelfile) #users's labels for the sensor readings

#parse time, break into chunks
studydata$timestamp=as.POSIXct(studydata$timestamp)
halfhoursecs=60*30
studydata$timechunk=as.POSIXct(round(as.numeric(studydata$timestamp)/halfhoursecs)*halfhoursecs,origin="1970-01-01",tz="UTC")

#estimate ambient temperature as 10th percentile of all sensors
timemodes=ddply(studydata,.(timechunk),function(timeslice){
  tempquant=quantile(timeslice$value,c(0.10))
  names(tempquant)=NULL

  return(c(amb_temp=tempquant))
})

studydata=merge(timemodes,studydata)
studydata=studydata[order(studydata$filename,studydata$timestamp),]
studydata$temp_c=studydata$value-studydata$amb_temp

#generate ml features from data
studyfeats=ddply(studydata,.(filename),makefeatures)

#format userlabel data
userlabels$cooking_label=as.numeric(userlabels$cooking_label=="True")
userlabels$timestamp=as.POSIXct(userlabels$timestamp)


# Drop labels for users that did not complete labelling (labelled less than other users)
#
# MP: this was commented out 2016-03 to support partial labelling.
#
# userlabels$count=1
# labelcounts=aggregate(count~email,userlabels,sum)
# complete=labelcounts$email[labelcounts$count==max(labelcounts$count)]
# userlabels=userlabels[userlabels$email%in%complete,]

#average labels across users
meanlabels=aggregate(cooking_label~filename+timestamp,userlabels,mean)
names(meanlabels)[3]=c("meanlabel")
meanlabels$combinedlabel=as.numeric(meanlabels$meanlabel>0.5)

#combine labels and ml features
meanlabels=merge(meanlabels,studyfeats)

print("Making folds")

#use SL to learn mapping between features and labels
folds <- make_folds(cluster_id=meanlabels$filename)

print("Made folds")
print("Learning")

# Original stack of algorithms:
# sl <- origami_SuperLearner(
#     meanlabels$combinedlabel,
#     meanlabels[,FEATURE_NAMES],
#     folds=folds,
#     SL.library=c("SL.rpart", "SL.glm", "SL.mean", "SL.glmnet"),
#     family=binomial())

# Simpler stack. Much faster. Within something like 5% of the full stack.
sl <- origami_SuperLearner(
    meanlabels$combinedlabel,
    meanlabels[,FEATURE_NAMES],
    folds=folds,
    SL.library=c("SL.glm"),
    family=binomial())



#SL might produce warnings if some algorithms are not behaving well.

print("Learned")
print("Predicting")

#predict labels on full dataset
studyfeats$pred <- predict(sl,studyfeats[,FEATURE_NAMES])$pred

print("Predicted")

#OUTPUT
#predicted labels for full dataset
write.csv(studyfeats,file=outputfile,row.names=F)
#save(studyfeats,file="studydata_ml.rdata")
