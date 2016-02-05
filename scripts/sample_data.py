import csv
import os.path
import shutil

for i in range(1000):
  shutil.copyfile('../sample_data/sample.csv', '../sample_data/mega/sample'+str(i)+'.csv')