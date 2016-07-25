library(pspline)
library(caTools)

makefeatures=function(senlabs){
  
  #stuff we need
  senlabs$index=1:nrow(senlabs)
  senlabs$timenum=as.numeric(senlabs$timestamp)
  
  mintemp=min(senlabs$temp_c)-1
  samprate=mean(as.numeric(difftime(senlabs$timestamp[-1],senlabs$timestamp[-1*nrow(senlabs)],units="secs")))
  
  #should maybe be absolute temperature
  senlabs$left=c(0,diff(senlabs$temp_c))*samprate
  senlabs$right=c(diff(senlabs$temp_c),0)*samprate
  
  #spline smoothing
  spmod=smooth.Pspline(senlabs$timenum,senlabs$temp_c,method="4")
  
  senlabs$slope=predict(spmod,senlabs$timenum,nderiv=1)*samprate
  senlabs$curvature=predict(spmod,senlabs$timenum,nderiv=2)*samprate^2
  senlabs$smoothpred=predict(spmod,senlabs$timenum,nderiv=0)
  
  senlabs$temp_sm=senlabs$temp_c-senlabs$smoothpred
  senlabs$leftsmoothed=c(0,diff(senlabs$smoothpred))*samprate
  senlabs$rightsmoothed=c(diff(senlabs$smoothpred),0)*samprate
  
  #now on log scale
  logspmod=smooth.Pspline(senlabs$timenum,log(senlabs$temp_c-mintemp),method="4")
  
  senlabs$logslope=predict(logspmod,senlabs$timenum,nderiv=1)*samprate
  senlabs$logcurvature=predict(logspmod,senlabs$timenum,nderiv=2)*samprate^2
  senlabs$logsmoothpred=predict(logspmod,senlabs$timenum,nderiv=0)
  
  senlabs$leftlogsmoothed=c(0,diff(senlabs$logsmoothpred))*samprate
  senlabs$rightlogsmoothed=c(diff(senlabs$logsmoothpred),0)*samprate
  
  
  #moving averages
  #hour long windows
  window=1+ceiling((60*60)/samprate)
  
  senlabs$rmin=runmin(senlabs$temp_c,window,align="right")
  senlabs$rmax=runmax(senlabs$temp_c,window,align="right")
  senlabs$rmean=runmean(senlabs$temp_c,window,align="center")
  
  senlabs$temp_rmin=senlabs$temp_c-senlabs$rmin
  senlabs$temp_rmax=senlabs$temp_c-senlabs$rmax
  senlabs$temp_rmean=senlabs$temp_c-senlabs$rmean
  
  senlabs$ismax=senlabs$rmax==senlabs$temp_c
  maxes=which(senlabs$ismax)
  senlabs$lastmaxindex=rep(maxes,diff(c(maxes,nrow(senlabs)+1)))
  senlabs$lastmax=senlabs$temp_c[senlabs$lastmaxindex]
  senlabs$slopefrommax=ifelse(senlabs$lastmaxindex==senlabs$index,0,(senlabs$temp_c-senlabs$lastmax)/(senlabs$index-senlabs$lastmaxindex))*samprate
  
  #try to fit an exponential to cooling
  senlabs$expdecay=ifelse(senlabs$temp_c==senlabs$lastmax,0,-(samprate/(senlabs$index-senlabs$lastmaxindex))*log((senlabs$temp_c-mintemp)/(senlabs$lastmax-mintemp)))
  decreasing=senlabs[senlabs$right<=0&senlabs$left<=0,]
  z=log((decreasing$right/samprate+decreasing$temp_c-mintemp)/(decreasing$temp_c-mintemp))
  lambda=mean(z)
  
  senlabs$exppred=(senlabs$temp_c-senlabs$left/samprate-mintemp)*exp(lambda)
  senlabs$expresid=senlabs$temp_c-senlabs$exppred-mintemp
  senlabs$lexpresid=senlabs$exppred/(senlabs$temp_c-mintemp)
  
  #expsub=which(senlabs$lastmax!=senlabs$temp_c)
  #expmod=nls(temp_c ~ lastmax * exp(-1*lambda*(index-lastmaxindex)),data=senlabs[expsub,],start=list(lambda=1),trace=T)
  #senlabs$expresid=0
  #senlabs$expresid[expsub]=resid(expmod)
  
  senlabs$ismin=senlabs$rmin==senlabs$temp_c
  mins=which(senlabs$ismin)
  senlabs$lastminindex=rep(mins,diff(c(mins,nrow(senlabs)+1)))
  senlabs$lastmin=senlabs$temp_c[senlabs$lastminindex]
  senlabs$slopefrommin=ifelse(senlabs$lastminindex==senlabs$index,0,(senlabs$temp_c-senlabs$lastmin)/(senlabs$index-senlabs$lastminindex))*samprate
  senlabs$expgrowth=ifelse(senlabs$temp_c==senlabs$lastmin,0,(1/(senlabs$index-senlabs$lastminindex))*log((senlabs$temp_c-mintemp)/(senlabs$lastmin-mintemp)))
  
  senlabs
}

FEATURE_NAMES=c("amb_temp","value", "temp_c", "left", 
                "right", "slope", "curvature", "smoothpred", 
                "temp_sm", "leftsmoothed", "rightsmoothed", "logslope", "logcurvature", 
                "logsmoothpred", "leftlogsmoothed", "rightlogsmoothed", "rmin", 
                "rmax", "rmean", "temp_rmin", "temp_rmax", "temp_rmean", "ismax", 
                "lastmaxindex", "lastmax", "slopefrommax", "expdecay", "exppred", 
                "expresid", "lexpresid", "ismin", "lastminindex", "lastmin", 
                "slopefrommin", "expgrowth")

