import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


def create_model(zipcode):
    # Importing the dataset to a pandas dataframe
    df = pd.read_csv('data/kc_house_data.csv')

    # Dropping the date column - correlates poorly to sale price
    df.drop('date', axis=1, inplace=True)

    # Dropping columns that poorly correlate to price and detract from the user experience
    df.drop(['id', 'yr_built', 'yr_renovated', 'long', 'sqft_lot', 'sqft_lot15', 'condition'], axis=1,
            inplace=True)

    # cleaning up records with anomalous and/or outlier values...
    # Dropping all rows with 0 bedrooms
    df.drop(df[df['bedrooms'] == 0].index, inplace=True)

    # Dropping all rows with 0 bathrooms
    df.drop(df[df['bathrooms'] == 0].index, inplace=True)

    # Changing number of bedrooms at index 15870 from 33 to 3
    df.at[15870, 'bedrooms'] = 3

    # approximating values for latitude and sqft_living15 using user input values..
    # selecting the median lat and sqft_living15 where zipcode matches user input..
    latitude = df[df['zipcode'] == zipcode]['lat'].median()
    sqftliving15 = df[df['zipcode'] == zipcode]['sqft_living15'].median()

    # Creating the train & test split
    X = df.drop('price', axis=1)
    y = df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Instantiating the model
    model = RandomForestRegressor(n_jobs=-1,
                                  random_state=42)
    model.fit(X_train, y_train)

    return model, model.score(X_test, y_test), latitude, sqftliving15
