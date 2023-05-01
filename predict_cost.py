import joblib
 
def predict(data):
    lr = joblib.load('lr_model.sav')
    return lr.predict(data)