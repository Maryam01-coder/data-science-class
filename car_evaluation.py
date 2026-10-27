import streamlit as st
import pandas as pd
import joblib
import numpy as np

#set page config
st.set_page_config(
  page_title="Jiji Car Evaluation",
  page_icon="🚗",
  layout="centered"
)

@st.cache_resource
def load_model_artifact():
  try:
    model = joblib.load("rm_model_car_price_prediction.pkl")
    scaler = joblib.load("scaler_features.pkl")
    feature = joblib.load("featured_columns.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    ordinal_encoder = joblib.load("ordinal_encoder.pkl")
    
    return model, scaler, feature, label_encoder, ordinal_encoder
  except FileNotFoundError as e:
    st.error(f"Model artifact not found: {e}")
    st.stop()
  except Exception as e:
    st.error(f"An error occured: {e}")
    st.stop()

@st.cache_data
def load_dataset():
  try:
    df = pd.read_csv("cleaned_jiji_car_dataset.csv")
    return df
  except FileNotFoundError as e:
    st.error(f"Dataset not found: {e}")
    st.stop()
    

def get_filtered_option(df, model=None, make=None, condition=None):
  filtered_df = df.copy()
  
  if model:
    filtered_df = filtered_df[filtered_df["model"] == model]
  
  if make:
    filtered_df = filtered_df[filtered_df["make"] == make]
  
  if condition:
    filtered_df = filtered_df[filtered_df["condition"] == condition]
    
  options = {
    "years": sorted(filtered_df["year"].unique().tolist(), reverse=True),
    "makes": sorted(filtered_df["make"].unique().tolist()),
    "models": sorted(filtered_df["model"].unique().tolist() if make else sorted(df["model"].unique().tolist())),
    "conditions": sorted(filtered_df["condition"].unique().tolist() if make or model else sorted(df["condition"].unique().tolist())),
    "transmission": sorted(filtered_df["transmission"].unique().tolist() if make or model or condition else sorted(df["transmission"].unique().tolist()))
  }
  
  return options

def predict_car_price(car_data, model, scaler, label_encoder, ordinal_encoder, feature_columns):
  try:
    input_df = pd.DataFrame([car_data])
    
    columns = ["make", "model"]
    for col in columns:
      try:
        input_df[col + "_encoded"] = label_encoder[col].transform(input_df[col])
      except Exception as e:
        st.warning(f"Unknown {col}: {car_data[col]}. Using default encoding.")
        input_df[col + "_encoded"] = 0
        

    try:
      encoded_ordinals = ordinal_encoder.transform(input_df[["condition", "transmission"]])
      input_df["condition_encoded"] = encoded_ordinals[0][0]
      input_df["transmission_encoded"] = encoded_ordinals[0][1]
      
    except Exception as e:
      st.warning(f"Unknown condition or transmission. Using default encoding.")
      input_df["condition_encoded"] = 0
      input_df["transmission_encoded"] = 0
        
    feature_dict = {
      "year": car_data["year"],
      "make_encoded": input_df["make_encoded"].values[0],
      "model_encoded": input_df["model_encoded"].values[0],
      "condition_encoded": input_df["condition_encoded"].values[0],
      "transmission_encoded": input_df["transmission_encoded"].values[0]
    }
    
    features = np.array([[feature_dict[col] for col in feature_columns]]) 
    
    feature_scale = scaler.transform(features)

    predicted_price = model.predict(feature_scale)[0]
    
    margin_percentage = 15
    min_predicted_price = predicted_price * (1 - margin_percentage)
    max_predicted_price = predicted_price * (1 + margin_percentage)
    
    return {
      "predicted_price": predicted_price,
      "min_predicted_price": min_predicted_price,
      "max_predicted_price": max_predicted_price
    }
  except Exception as e:
    st.error(f"An error occured: {e}")


def main():
  st.title("Jiji Car Evalaution")
  st.write("Fill all the fields and get immediate car price result.")
  
  model, scaler, feature, label_encoder, ordinal_encoder = load_model_artifact()
  
  df = load_dataset()
  
  #initialize session
  if "seleceted_make" not in st.session_state:
    st.session_state.selected_make = None
  
  if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
  
  if "selected_condition" not in st.session_state:
    st.session_state.selected_condition = None
    
  if "show_result" not in st.session_state:
    st.session_state.show_result = False
  
  options = get_filtered_option(df)
  
  make = st.selectbox(
    "*Make",
    options=[""] + options["makes"],
    format_func=lambda x: "Select Make" if x == "" else x
  )
  
  if make and make != st.session_state.selected_make:
    st.session_state.selected_make = make
    st.session_state.selected_model = None
    st.session_state.selected_condition = None
    st.session_state.show_result = False
  
  if make:
    options = get_filtered_option(df, make=make)
  
  model_name = st.selectbox(
    "*Make",
    options=[""] + options["models"],
    format_func=lambda x: "Select Make" if x == "" else x,
    disabled=not make
  )
  
  if model_name and model_name != st.session_state.selected_model:
    st.session_state.selected_model = model_name
    st.session_state.selected_condition = None
    st.session_state.show_result = False
  
  if make and model_name:
    options = get_filtered_option(df, make=make, model=model_name)
    
  year = st.selectbox(
    "*Year",
    options=[""] + options["years"],
    format_func=lambda x: "Select Year" if x == "" else str(x),
    disabled=not (make and model_name)
  )
  
  if year:
    st.session_state.show_result = False
    
  condition = st.selectbox(
    "*Condition",
    options=[""] + options["conditions"],
    format_func=lambda x: "Select Condition" if x == "" else x,
    disabled=not (make and model_name and year)
  )
  
  if condition and condition != st.session_state.selected_condition:
    st.session_state.selected_condition = condition
    st.session_state.show_result = False
  
  if make and model_name and condition:
    options = get_filtered_option(df, make=make, model=model_name, condition=condition)
  
  transmission = st.selectbox(
    "*Transmission",
    options=[""] + options["transmission"],
    format_func=lambda x: "Select Transmission" if x == "" else x,
    disabled=not (make and model_name and year and condition)
  )
  
  if transmission:
    st.session_state.show_result = False
  
  #get result
  if st.button("Get Result"):
    if not all([make, model_name, year, condition, transmission]):
      st.warning("Please fill all the fields")
    else:
      car_data = {
        "make": make,
        "model": model_name,
        "year": int(year),
        "condition": condition,
        "transmission": transmission
      }
      
      with st.spinner("Calculating the predicted price..."):
        result = predict_car_price(car_data, model, scaler, label_encoder, ordinal_encoder, feature)
      
      if result is not None:
            st.session_state.show_result = True
            st.session_state.result = result
            st.session_state.car_data = car_data
  
  #display result
  if st.session_state.show_result and "result" in st.session_state:
    result = st.session_state.result
    car_data = st.session_state.car_data
    
    #display car detail
    st.markdown("---")
    st.subheader(f"Estimated car price: {car_data['year']} {car_data['make']} {car_data['model']}")
    
    st.markdown("---")
    st.success(f"## ₦{result['predicted_price']:,.0f}")
    
    #price range
    st.markdown("---")
    st.write(f"** Price range: {result['min_predicted_price']:,.0f} - {result['max_predicted_price']:,.0f}")
    
    #display car detail
    st.write(f"** Condition {car_data['condition']} | ** Transmission {car_data['transmission']}")
      

if __name__ == "__main__":
  main()