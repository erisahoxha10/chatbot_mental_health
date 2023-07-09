import mysql.connector
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from sklearn.tree import *
import pandas as pd


SYMPTOMS = ['feeling_nervous', 
            'panic', 
            'breathing_rapidly', 
            'sweating', 
            'trouble_in_concentration',
            'having_trouble_in_sleeping', 
            'having_trouble_with_work', 
            'hopelessness', 
            'anger', 
            'over_react', 
            'change_in_eating', 
            'suicidal_thought', 
            'feeling_tired',
            'close_friend',
            'social_media_addiction',
            'weight_gain',
            'introvert',
            'popping_up_stressful_memory',
            'having_nightmares',
            'avoids_people_or_activities',
            'feeling_negative',
            'trouble_concentrating',
            'blamming_yourself',
            'hallucinations',
            'repetitive_behaviour',
            'seasonally',
            'increased_energy']

def createConnection(host = "localhost", user = "root",passwd = "root", database = "chatbot"):
    myconn = mysql.connector.connect(host = "localhost", user = "root",passwd = "root", database = "chatbot")
    return myconn

myconn = createConnection()

def createDecisionTree(symptoms_array, age=25):
    query = "select * from chatbot_mental_issues where "
    for symptom in symptoms_array:
        query = query + symptom + " = 1 and "
    query = query + " age <" + str(age+5) + " and age > " + str(age-5)
    # cur = myconn.cursor()
    # cur.execute(query)
    rows = pd.read_sql(query, myconn)
    myconn.close()

    # Separate features (symptoms and age) and the target variable (disease)
    X = rows.iloc[:, 1:-1]  # Features (symptoms and age)
    y = rows['Disorder']  # Target variable

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # print(X_test)
    # decision_tree = DecisionTreeClassifier(max_depth=20, splitter='random', min_samples_split=10)
    decision_tree = DecisionTreeClassifier()

    # Train the decision tree model
    decision_tree.fit(X_train, y_train)

    # Make predictions on the testing set
    y_pred = decision_tree.predict(X_test)

    # Calculate the accuracy of the model
    accuracy = accuracy_score(y_test, y_pred)
    # print('Accuracy:', accuracy)

    tree_text = export_text(decision_tree, feature_names=list(X.columns))
    return decision_tree, tree_text, list(X.columns)