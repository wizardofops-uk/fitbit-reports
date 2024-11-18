#!/bin/python3

##############
# Initialise #
##############

# Import modules
import os, json
import pandas as pd
import pdfkit as pdf
from IPython.display import display, HTML
import matplotlib.pyplot as plt
from PIL import Image
import warnings

# Global settings
root_folder = './dataset/api'
warnings.filterwarnings('ignore')

# Load data
with open("./dataset/api/profile.json", 'r') as file:
  json_prof = json.load(file)
with open("./dataset/api/nutrition.json", 'r') as file:
  json_nutri = json.load(file)
with open("./dataset/api/water.json", 'r') as file:
  json_water = json.load(file)
with open("./dataset/api/weight.json", 'r') as file:
  json_weight = json.load(file)
with open("./dataset/api/activity.json", 'r') as file:
  json_activ = json.load(file)

#############
# Functions #
#############

# Function for displaying a bar graph
def bar_graph(df,xaxis,yaxis,title,filename):
  df = df.groupby(xaxis, as_index=False).agg({yaxis: 'sum'})
  plt.bar(df[xaxis], df[yaxis])
  plt.title(title)
  plt.xlabel(xaxis)
  plt.ylabel(yaxis)
  plt.xticks(rotation=80)
  plt.grid(True)
  plot_image_path = f"{root_folder}/{filename}" 
  plt.savefig(plot_image_path, format='png') 
  return plot_image_path

# Function for returning nutrition data
def get_nutrition(json_data, keys):
  flattened_data = []
  for date, values in json_data.items():
    for food in values.get('foods', []):
      entry = {'Date': date}
      for key, friendly_name in keys.items():
        path_list = key.strip("][").replace("'", "").split("][")
        data = food
        for p in path_list:
          if isinstance(data, list):
            try:
              p = int(p)
              data = data[p]
            except (IndexError, ValueError):
              data = None
              break
          else:
            data = data.get(p, None)
            if data is None:
              break
        entry[friendly_name] = data
      flattened_data.append(entry)
  df = pd.DataFrame(flattened_data)
  df['Date'] = pd.to_datetime(df['Date'])
  return df

# Function for returning entry from JSON as a dataframe
def get_entry(json_data, path, key_name): 
  def get_value(data, path_list): 
    for key in path_list: 
      if isinstance(data, list): 
        try: 
          key = int(key) 
          data = data[key] 
        except (IndexError, ValueError): 
          return None
      else: 
        data = data.get(key, None) 
        if data is None: 
          return None 
    return data 
  path_list = path.strip("][").replace("'", "").split("][") 
  flattened_data = [] 
  for date, values in json_data.items(): 
    value = get_value(values, path_list) 
    if value is not None: 
      flattened_data.append({'Date': date, f"{key_name}": value}) 
  df = pd.DataFrame(flattened_data) 
  df['Date'] = pd.to_datetime(df['Date'])
  return df

def highlight_total(row): 
  return ['font-weight: bold' if row['Meal'] == 'Total' else '' for _ in row]

##############
# Dataframes #
##############

# Generate dataframes
df_water = get_entry(json_water, "['summary']['water']", "Water (ml)")
df_calsout = get_entry(json_activ, "['summary']['caloriesOut']", "Cals Out (kcal)")
df_weight = get_entry(json_weight, "['weight'][0]['weight']", "Weight (kg)")

# Nutrition parameters
meal_mapping = {
    1: 'Breakfast',
    2: 'Morning Snack',
    3: 'Lunch',
    4: 'Afternoon Snack',
    5: 'Dinner',
    6: 'Evening Snack'
}
nutri_keys = {
    "['loggedFood']['mealTypeId']": "Meal",
    "['loggedFood']['brand']": "Brand",
    "['loggedFood']['name']": "Name",
    "['loggedFood']['amount']": "Amount",
    "['loggedFood']['unit']['name']": "Unit",
    "['nutritionalValues']['calories']": "Cals (kcal)",
    "['nutritionalValues']['carbs']": "Carbs (g)",
    "['nutritionalValues']['fat']": "Fat (g)",
    "['nutritionalValues']['protein']": "Protein (g)"
}

# Generate Nutrition dataframe
df_nutri = get_nutrition(json_nutri, nutri_keys)
df_nutri['Meal'] = df_nutri['Meal'].map(meal_mapping)

# Add total row
day_total = df_nutri.groupby('Date').sum(numeric_only=True).reset_index() 
day_total['Meal'] = 'Total' 
day_total = pd.merge(day_total, df_water, on='Date', how='left')
day_total = pd.merge(day_total, df_calsout, on='Date', how='left')

# Sort the data
df = pd.concat([df_nutri, day_total], ignore_index=True) 
df = df.sort_values(by=['Date', 'Meal']).reset_index(drop=True) 
df['Day'] = df['Date'].dt.strftime('%A')
df.loc[df.duplicated(subset=['Date', 'Day']), ['Date', 'Day']] = ''
column_order = [
  'Date', 
  'Day', 
  'Meal', 
  'Brand', 
  'Name', 
  'Amount', 
  'Unit', 
  'Cals (kcal)', 
  'Carbs (g)', 
  'Fat (g)', 
  'Protein (g)', 
  'Cals Out (kcal)',
  'Water (ml)'
] 
df = df[column_order]
df[column_order[5]] = pd.to_numeric(df[column_order[5]], errors='coerce')
df[column_order[7]] = pd.to_numeric(df[column_order[7]], errors='coerce')
df[column_order[8]] = pd.to_numeric(df[column_order[8]], errors='coerce')
df[column_order[9]] = pd.to_numeric(df[column_order[9]], errors='coerce')
df[column_order[10]] = pd.to_numeric(df[column_order[10]], errors='coerce')
df[column_order[11]] = pd.to_numeric(df[column_order[11]], errors='coerce')
df = df.fillna('')

# Add new row after total
# df = pd.DataFrame(columns=df.columns)  
# for index, row in df.iterrows(): 
#   df = pd.concat([df, pd.DataFrame([row]), pd.DataFrame([['']*len(df.columns)], columns=df.columns)], ignore_index=True)

# Style the data
df_display = df.style.apply(highlight_total, axis=1).format({
  f'{column_order[5]}': '{:.0f}',
  f'{column_order[7]}': '{:.0f}',
  f'{column_order[8]}': '{:.2f}', 
  f'{column_order[9]}': '{:.2f}', 
  f'{column_order[10]}': '{:.2f}', 
})

# Generate HTML formatted dataframes
html_list = []
df_html = df_display.to_html()
html_list.append(df_html)

# Generate HTML report
html = """
<html>
  <head>
    <style> 
      body {font-family: Arial, sans-serif;}
      th, td {text-align: justify;}
    </style>
  </head>
<body>
  <h1>Report on Nutrition</h1>
"""
html += '<br />'.join(html_list)
html += '</body></html>'

html_path = f'{root_folder}/report.html'
with open(html_path, 'w') as f:
    f.write(html)

# Convert HTML to PDF
pdffile = f'{root_folder}/report.pdf'
pdfopt = { 'page-size': 'A4', 'orientation': 'Landscape' }
pdf.from_file(html_path, pdffile, options=pdfopt)
