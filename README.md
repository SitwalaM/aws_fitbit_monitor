# Fitbit Sleep and Heart Monitor on AWS

## Overview
Simple application that monitors my daily heart and sleep data using fitbit API.The main objective was to learn following key tools
* AWS Lambda functions
* APIs with Lambda functions
* AWS S3 Storage with lambda functions
* AWS SNS with Lambda functions
* AWS Secrets Manager

## Architecture
![Fitbit Monitor Architecture](https://github.com/SitwalaM/aws_fitbit_monitor/blob/main/images/architecture.png)

## Heart Data EDA
The following graphs are obtained from the data collected from the s3 bucket.

![Heart Rate Distribution](https://github.com/SitwalaM/aws_fitbit_monitor/blob/main/images/heart_dist.png)

### Let's see how this looks if we filter it by day

![bar chart](https://github.com/SitwalaM/aws_fitbit_monitor/blob/main/images/days_violin_chart.png)

![bar chart](https://github.com/SitwalaM/aws_fitbit_monitor/blob/main/images/days_bar_chart.png)

## Anomaly Detection using Isolation Forest

[Isolation forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) was used for anomaly detection. It's an unsupervised learning algorithm that uses tree splits to isolate outliers in a dataset. The key parameter to tune for this algorithm is the contamination, which represents the ration of anomalies in the sample. Here, the contamination was chosen to be 0.08 through observation of the results it produced. It basically sets a threshold for what is considered as abnormal. A good way to check if the contamination is too high is to inspect some anomalies that are within ranges of data points that are not flagged as anomalies.

```Bash
# fit and predict using isolation forest

clf = IsolationForest(contamination=0.08)
clf.fit(df[["heart_rate"]] )
pred = clf.predict(df[["heart_rate"]])
```

![classifier](https://github.com/SitwalaM/aws_fitbit_monitor/blob/main/images/classified.png)




## Acknowledgements/References
[Inspired by guide here](https://qiita.com/bmj0114/items/620cd32eb599f1b26ea5)

[Amazing guidance on all AWS services (YouTube)](https://www.youtube.com/channel/UCraiFqWi0qSIxXxXN4IHFBQ)

[How to use secrets manager with AWS lambda](https://github.com/endre-synnes/python_aws_course/tree/main/lambda_intro/04_secrets_and_databases_and_stuff)
