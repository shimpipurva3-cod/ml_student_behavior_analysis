import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

df = pd.read_csv("ml_student_behavior_dataset_50000.csv")
print("dataset Loaded successfully!")
print("-------------------------------------------")
print("Total Records:",len(df))
print("-------------------------------------------")
print("Dataset:")
print(df.head())
print("-------------------------------------------")
X=df[['study_hours','sleep_hours','screen_time','water_intake','marks']]
Y=df['behavior']
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.20,random_state=42,stratify=Y)
print("Training Records:",len(X_train))
print("Testing Records:",len(X_test))
print("-------------------------------------------")
model=DecisionTreeClassifier(random_state=42,max_depth=5)
model.fit(X_train,Y_train)
print("Model Training Completed!")
print("-------------------------------------------")
Y_pred=model.predict(X_test)
accuracy=accuracy_score(Y_test,Y_pred)
print("Accuracy Score:",round(accuracy*100,2),"%")
print("-------------------------------------------")
def predict_behavior(study_hours,sleep_hours,screen_time,water_intake,marks):
    new_data=pd.DataFrame([[study_hours,sleep_hours,screen_time,water_intake,marks]],
                          columns=[
                              'study_hours','sleep_hours','screen_time','water_intake','marks'
                          ])
    prediction=model.predict(new_data)
    return prediction[0]

if __name__ == '__main__':
    result=predict_behavior(5,7,3,2,83.4)
    print('Predicted Learning Behavior:',result)
print("-------------------------------------------")