import json
import datetime
import requests
import numpy as np
import boto3
from secrets import get_secret

# aws services clients
s3 = boto3.client("s3")
sns = boto3.client('sns')

# authentication for fitbit
access_token = get_secret("arn:aws:secretsmanager:us-east-1:673580324193:secret:api_access_token-rN4wU3")
headers = {"Authorization" : "Bearer " + access_token["fitbit_access_token"]}


yesterday = str(datetime.date.today() - datetime.timedelta(days=1))

# alarm thresholds for heart rate and sleep - email is only sent if heart rate is higher than thresh or sleep is less than thresh
sleep_thresh = 7
heart_thresh = 72

def get_heart_data(date_data): # This function will be handled by the lambda function mostly
    ''' 
    The functions gets the heart-rate data from the fitbit account for the specified day
    date_data: the date in string format YYYY-mm-dd
    Returns: Dictionary the day that was recorded for, dictionary for heart rate for one day, average_heart_rate
    '''
    http_request  =  "https://api.fitbit.com/1/user/-/activities/heart/date/"+ date_data + "/1d/15min.json"
    r = requests.get(http_request, headers=headers)
    data = r.json()
    df =  data['activities-heart-intraday']['dataset']
    
    times = []
    values = []
    for value in df:
        times.append(value['time'])
        values.append(value['value'])

    mean_on_day = round(np.array(values).mean(),3)
    
    return {'day': date_data, 
    'heart_data': df, 
    "average_heart_rate": mean_on_day }


def get_sleep_data(date_data):
    '''
    The functions gets the heart-rate data from the fitbit account for the specified day
    date_data:
    Returns: Dictionary of date_of_sleep, the original sleep_data in json,  sleep_duration_hrs
    '''   
    http_request= "https://api.fitbit.com/1.2/user/-/sleep/date/"+date_data+".json"
    r = requests.get(http_request, headers=headers)
    data = r.json()
    
    sleep_duration_hrs = round(data['sleep'][0]['duration']/(3600*1000),3)
    
    date_of_sleep = data['sleep'][0]['dateOfSleep']
    
    return {'date_of_sleep': date_of_sleep, 'sleep_data': data,  'sleep_duration_hrs':  sleep_duration_hrs}


date = yesterday 
heart_data = get_heart_data(date)
sleep_data = get_sleep_data(date)

# if heart_data_ mean > heart_thresh text phone, if sleep data is less than 6.5, text phone

fitbit_data = {"date": date , 'heart_data':  heart_data , "sleep_data":  sleep_data }
    



def sns_publish(message):
    '''
    Publish the email to the topic
    input: the string message to be published
    '''
    response = sns.publish(TopicArn="arn:aws:sns:us-east-1:673580324193:fitbit_notification",
                            Message=message,
                            MessageStructure='text',
                            Subject='Fitbit Notification')


def lambda_handler(event, context):

    bucket = "bucketfitbit"
    
    date = yesterday 

    heart_data = get_heart_data(date)

    sleep_data = get_sleep_data(date)

    fitbit_data = {"date": date , 'heart_data':  heart_data , "sleep_data":  sleep_data }


    # Send an email if heart rate goes above a threshold or sleep is below a certain amount

    if heart_data['average_heart_rate'] > heart_thresh and sleep_data['sleep_duration_hrs'] < sleep_thresh:
        message1 = "Your heart rate exceeded threshold yesterday, your average heart rate was: " + \
                   str(heart_data['average_heart_rate']) + " bpm"
        message2 = "You did not get enough sleep last night, you slept for: " + \
                   str(sleep_data['sleep_duration_hrs']) + "hrs"
        message = message1 + "\n" + message2
        sns_publish(message)
    
    elif heart_data['average_heart_rate'] > heart_thresh and sleep_data['sleep_duration_hrs'] > sleep_thresh :
        message = "Your heart rate exceeded threshold yesterday, your average heart rate was: " + \
                   str(heart_data['average_heart_rate']) + " bpm"
        sns_publish(message)

    elif sleep_data['sleep_duration_hrs'] < sleep_thresh and heart_data['average_heart_rate'] < heart_thresh  :
        message = "You did not get enough sleep last night, you slept for: " + \
                   str(sleep_data['sleep_duration_hrs']) + "hrs"
        sns_publish(message)
    else:
        pass


    # Load the data into s3 bucket
    fileName = date + ".json"

    uploadByteStream =bytes(json.dumps(fitbit_data, indent=4, sort_keys = True).encode("UTF-8"))

    s3.put_object(Bucket= bucket, Key = fileName, Body =  uploadByteStream)

    return {
        'statusCode': 200,
        'body': json.dumps("Code run successfully, " + "sleep: " + str(sleep_data['sleep_duration_hrs'])
                            + "  heart rate: " +  str(heart_data['average_heart_rate']) )
    }
    

    
