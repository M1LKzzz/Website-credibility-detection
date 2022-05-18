from matplotlib.pyplot import axis
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from trust.phishing_detection import feature_extraction

def phishing_detect(url):

    urls=pd.read_csv("trust/phishing_detection/dataset.csv")

    urls_without_labels = urls.drop('label',axis=1)
    labels = urls['label']

    data_train, data_test, labels_train, labels_test = train_test_split(urls_without_labels.values,labels.values,test_size=0.30,random_state=110)

    random_forest_classifier = RandomForestClassifier()
    random_forest_classifier.fit(data_train,labels_train)

    # print(random_forest_classifier.feature_importances_)

    x_input = []
    x_input = feature_extraction.generate_data_set(url)

    for i in range(len(x_input)):
        x_input[i]=-x_input[i]
    

    x_input = np.array(x_input).reshape(1,-1)

    # prediction = random_forest_classifier.predict(x_input)
    # if prediction == 1:
    #     return "Phishing Website"
    # else:
    #     return "Not Phishing Website"

    try:
        prediction = random_forest_classifier.predict(x_input)
        if prediction == 1:
            return "Phishing Website"
        else:
            return "Not Phishing Website"
    except:
        return  "Not Phishing Website--+"

# if __name__ == '__main__':
#     result = phishing_detect("https://www.baidu.com/")
#     print(result)
