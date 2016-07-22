#
# Usage: Rscript ml_script.R ../data/studydata.csv ../data/userlabels.csv ../data/studydata_ml.csv
# Usage: Rscript ml_script.R <user_labels.csv> <study_data_dir> <output_dir>
#
# Trains the labeler using `user_labels.csv`, outputing predicted labels for each file in 
# `study_data_dir` into a corresponding file in `output_dir`.
#
# Does not support nested directories.
#
# Should be invoked from the `ml_labeler` directory
#

library(plyr)
library(origami)
source("features.R")

args = commandArgs(trailingOnly=TRUE)

userlabelfile=args[1] # e.g. userlabels.csv
studydata_dir=args[2] # e.g. studydata.csv
output_dir=args[3]

print("Reading inputs")

# Generated from querydump.sql
userlabels=read.csv(userlabelfile)

print("Making training features")

# Marshall columns
userlabels$cooking_label=as.numeric(userlabels$cooking_label=="t")
userlabels$timestamp=as.POSIXct(userlabels$timestamp)

# Adds necessary columns to call `makefeatures` to input CSV files
# (both user_labels and study_data)
datapoints_to_features = function(datapoints) {
    datapoints$timestamp=as.POSIXct(datapoints$timestamp)

    # Parse time, break into chunks
    datapoints$timestamp = as.POSIXct(datapoints$timestamp)
    halfhoursecs = 60*30
    datapoints$timechunk=as.POSIXct(
        round(as.numeric(datapoints$timestamp)/halfhoursecs)*halfhoursecs,
        origin="1970-01-01",
        tz="UTC")

    # Estimate ambient temperature as 10th percentile of all sensors
    timemodes=ddply(datapoints,.(timechunk), function(timeslice) {
      tempquant=quantile(timeslice$value,c(0.10))
      names(tempquant)=NULL
      return(c(amb_temp=tempquant))
    })

    datapoints=merge(timemodes,datapoints)
    datapoints=datapoints[order(datapoints$filename,datapoints$timestamp),]
    datapoints$temp_c=datapoints$value-datapoints$amb_temp

    # Generate ml features from data
    features = ddply(datapoints,.(filename), makefeatures)
    return(features)
}

training_features <- datapoints_to_features(userlabels)

# Average labels across users
meanlabels = aggregate(cooking_label~filename+timestamp, userlabels, mean)
names(meanlabels)[3] = c("meanlabel")
meanlabels$combinedlabel=as.numeric(meanlabels$meanlabel>0.5)

# Combine labels and ml features
meanlabels=merge(meanlabels, training_features)

# Use SL to learn mapping between features and labels
folds <- make_folds(cluster_id=meanlabels$filename)

print("Training model")

# Original stack of algorithms:
# algorithms = c("SL.rpart", "SL.glm", "SL.mean", "SL.glmnet")

# Simpler stack. Much faster. Within something like 5% of the full stack.
algorithms = c("SL.glm")
sl <- origami_SuperLearner(
    meanlabels$combinedlabel,
    meanlabels[,FEATURE_NAMES],
    folds=folds,
    SL.library=algorithms,
    family=binomial())

print("Learned")

print("Predicting")

for (filename in list.files(studydata_dir)) {
    studydata = read.csv(file.path(studydata_dir, filename))
    studyfeats <- datapoints_to_features(studydata)
    studyfeats$pred <- predict(sl,studyfeats[,FEATURE_NAMES])$pred
    print(paste("Predicted ", filename))
    write.csv(studyfeats, file=file.path(output_dir, filename), row.names=F)
}