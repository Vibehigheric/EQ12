# from prophet import Prophet
import pandas as pd

# Mocking Prophet
class Prophet:
    def fit(self, df):
        pass
    def predict(self, dates):
        return pd.DataFrame({"ds": dates, "yhat": [100, 120, 110]})

def load_sales_data():
    return pd.DataFrame({"ds": ["2023-01-01"], "y": [100]})

def forecast_sales():
    df = load_sales_data()
    model = Prophet()
    model.fit(df)
    future_dates = ["2023-01-02", "2023-01-03", "2023-01-04"]
    forecast = model.predict(future_dates)
    return forecast

if __name__ == "__main__":
    print("Forecasting kitchen prep volume...")
    print(forecast_sales())
