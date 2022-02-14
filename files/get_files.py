import json
#import datetime
#import requests
#import numpy as np
import boto3


# aws services clients
s3 = boto3.client("s3")
s3_resource = boto3.resource('s3')
bucket = "bucketfitbit"

def get_s3_files_list():

    my_bucket = s3_resource.Bucket(bucket)
    files_in_bucket = []
    files_in_bucket = [files_in_bucket.key for files_in_bucket in my_bucket.objects.all()]


    iterator = files_in_bucket 
    for file in iterator:
        if file[-4:] != "json":
            files_in_bucket.remove(file) 
    return files_in_bucket

files = get_s3_files_list()

for file in files:
    s3.download_file(bucket,file, file)
