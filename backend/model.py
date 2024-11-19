import pandas as pd
import numpy as np
import pickle
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, recall_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

#used 'latin1' as encoding since this dataset contain some special characters
SC=pd.read_csv("backend/venv/DataCoSupplyChainDataset.csv", encoding='latin1')

#checking the lengths of the array dimensions
print(SC.shape)

#checking the number of variables and their types
print(SC.info())

#checking the top 10 rows in the dataset
print(SC.head(10))

#Returning statistical description of the data in the dataset
print(SC.describe())

#observation of the late and ontime delivery
column_name = 'Delivery Status'
advanced_shipping_data = 'Advance shipping'
count_advanced_shipping_data = SC[SC[column_name] == advanced_shipping_data].shape[0]

late_delivery_data = 'Late delivery'
count_late_delivery_data = SC[SC[column_name] == late_delivery_data].shape[0]

on_time_delivery_data = 'Shipping on time'
count_on_time_delivery_data = SC[SC[column_name] == on_time_delivery_data].shape[0]

canceled_shipping_data = 'Shipping canceled'
count_canceled_shipping_data = SC[SC[column_name] == canceled_shipping_data].shape[0]

print(f"Advanced shipping count:  {count_advanced_shipping_data}")
print(f"Late Delivery count:  {count_late_delivery_data}")
print(f"On time delivery count: {count_on_time_delivery_data}")
print(f"Canceled shipping data: {count_canceled_shipping_data}")

print("Total")
print(count_advanced_shipping_data + count_late_delivery_data + count_on_time_delivery_data +count_canceled_shipping_data)


#Data Cleaning

#Checking the number of missing values for each variable
print(np.sum(SC.isna()))

#Cleaning
#Dropping unimportant columns
SC_Data = SC.drop(['Type','Benefit per order','Sales per customer','Category Id','Category Name',
                   'Customer Email','Customer Fname','Customer Id','Customer Lname','Customer Password',
                   'Customer Segment','Customer Street','Customer State','Customer Zipcode','Department Id',
                   'Department Name','Market','Order Customer Id','Order Id','Order Item Cardprod Id','Order Item Discount',
                   'Order Item Discount Rate','Order Item Id','Order Item Product Price','Order Item Profit Ratio',
                   'Sales','Order Item Total','Order Profit Per Order','Order Region','Order State',
                   'Order Status','Order Zipcode','Product Card Id','Product Category Id','Product Description',
                   'Product Image','Product Name','Product Price','Product Status'],axis=1)
print(SC_Data.shape)

#Checking column names after dropping
print(SC_Data.columns)

#Replacing the spaces and paranthesis with the _ sign
SC_Data.columns = [col.lower().replace(' ', '_') for col in SC_Data.columns]
SC_Data.rename(columns=lambda x: x.replace("(", "").replace(")", ""), inplace = True)

#Data Modelling

#Create train data set
train_dataSC = SC_Data.copy()

#Create a new column for orders with "late Delivery" 
train_dataSC['late_delivery'] = np.where(train_dataSC['delivery_status'] == 'Late delivery', 1,0)

#Drop columns with repeated values and unaffected ones
train_dataSC = train_dataSC.drop(['delivery_status', 'late_delivery_risk','days_for_shipping_real', 'days_for_shipment_scheduled','shipping_date_dateorders'], axis = 1)

print(train_dataSC.info())

#create the labelencoder object
le = preprocessing.LabelEncoder()

#Changing all object types into 'int'
train_dataSC['customer_city'] = le.fit_transform(train_dataSC['customer_city'])
train_dataSC['customer_country'] = le.fit_transform(train_dataSC['customer_country'])
train_dataSC['order_city'] = le.fit_transform(train_dataSC['order_city'])
train_dataSC['order_country'] = le.fit_transform(train_dataSC['order_country'])
train_dataSC['shipping_mode'] = le.fit_transform(train_dataSC['shipping_mode'])
train_dataSC['order_date_dateorders'] = le.fit_transform(train_dataSC['order_date_dateorders'])

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le,  f)

#checking the top 10 rows in the dataset
print(train_dataSC.head(10))

#Train/test data split
xlatedelivery = train_dataSC.loc[:, train_dataSC.columns != 'late_delivery']
ylatedelivery = train_dataSC['late_delivery']
xlatedelivery_train, xlatedelivery_test, ylatedelivery_train, ylatedelivery_test = train_test_split(xlatedelivery, ylatedelivery, test_size = 0.3, random_state = 42)

#Standardizing the data
sc = StandardScaler()
xlatedelivery_train = sc.fit_transform(xlatedelivery_train)
xlatedelivery_test = sc.fit_transform(xlatedelivery_test)

#Random Forest Classification
model_latedelivery = RandomForestClassifier(n_estimators = 100, max_depth = 10, random_state = 0)

#fitting train data for prediction of late delivery
model_latedelivery = model_latedelivery.fit(xlatedelivery_train, ylatedelivery_train)
ylatedelivery_pred = model_latedelivery.predict(xlatedelivery_test)

#accuracy for prediction of late delivery
accuracy_latedelivery = accuracy_score(ylatedelivery_pred, ylatedelivery_test)

#recall score for prediction of late delivery
recall_latedelivery = recall_score(ylatedelivery_pred, ylatedelivery_test)

#confusion matrix for predction of late delivery
conf_latedelivery = confusion_matrix(ylatedelivery_test, ylatedelivery_pred)

#f1 score for prediction of late delivery
f1_latedelivery = f1_score(ylatedelivery_test, ylatedelivery_pred)

print("Model parameters used are :" , model_latedelivery)
print("Accuracy of late delivery status is :", (accuracy_latedelivery)*100, "%")
print("Recall score of late delivery status id :", (recall_latedelivery)*100, "%")
print("F1 score of late delivery status is :", (f1_latedelivery)*100, "%")
print("Confusion Matrix of late delivery status is :\n", (conf_latedelivery))
    

if(ylatedelivery_pred[0] == 1):
    print('Late Delivery')
else:
    print('Not a late delivery')

pickle.dump(model_latedelivery, open("model.pkl", "wb"))