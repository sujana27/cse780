# REF_DATE                            int64
# GEO                                object
# DGUID                              object
# Economic family type               object
# Household food security status     object
# Statistics                         object
# UOM                                object
# UOM_ID                              int64
# SCALAR_FACTOR                      object
# SCALAR_ID                           int64
# VECTOR                             object
# COORDINATE                         object
# VALUE                             float64
# STATUS                             object
# SYMBOL                            float64
# TERMINATED                        float64
# DECIMALS                            int64
# dtype: object


# "Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan",
# "Alberta", "Newfoundland and Labrador", "Prince Edward Island", "British Columbia"


import plotnine as plt9
from plotnine import aes
import pandas as pd
import numpy as np
from shiny import *


# read in data
df = pd.read_csv("13100834.csv")

# Function for UI
def create_ui():
  # create our ui object
  app_ui = ui.page_fluid(
    
    # App title ----
    ui.panel_title("Food Security Status in Canada"),
    
    # Subtitle
    ui.markdown(
        """
        Dataset: [Food insecurity by economic family type](https://open.canada.ca/data/en/dataset/a98ab5ae-c484-41d0-815c-b71562ed0704)
        
        This graphical representation illustrates for food insecurity status in Canada for different provinces. Select the food security severity level from the drop-down and select province from the checkbox list to individually see the result. Check all the check-boxes to see a combined result to visualize the comparison. As an example: all provinces are checked and food Insecure level is selected by default. Overall, we can see that PEI is leading in term of food insecurity and Quebec is the least.
        
        """
    ),
    ui.row(
        # line chart output
        
        # controls
        ui.column(2,
           
          ui.markdown(
            """
            **Select food secure status and province to explore**
            """
          ),
          ui.input_select(
              "secure_status", "Food Secure Status",
              choices=["Food insecure", "Food secure", "Food insecure, severe", "Food insecure, marginal"],
              selected=["Food insecure"]
          ),
          ui.input_checkbox_group(
              "geo_locations", "Locations",
              choices=["Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta", "Newfoundland and Labrador", "Prince Edward Island", "British Columbia"],
              selected=["Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta", "Newfoundland and Labrador", "Prince Edward Island", "British Columbia"]
          )
        ),
        ui.column(10, ui.output_plot("barplot")), 
    )
  )
  return app_ui

ui_obj = create_ui()


# Function to make the plot
def create_plot(data):
  plot = (
    plt9.ggplot(data = data, mapping = plt9.aes(x = 'REF_DATE', y='VALUE', color='GEO', group=data['GEO'])) +
      plt9.theme_minimal() +
      plt9.geom_line(linetype = "solid")+
      plt9.geom_point()+
      #gg.geom_line(aes(linetype=data['GEO']))+
      #gg.scale_linetype_manual(values=c("twodash", "dotted"))
      plt9.labs(x = "Year", y = "Avg. Food Status(%)", title="Food-Security Status over the years") +
      plt9.geom_point(aes(shape=data['GEO']))+
      plt9.theme(panel_grid_major_x = plt9.element_blank(), panel_grid_minor_x = plt9.element_blank())
  )
  return plot.draw()


def generate_mean_of_data(cl_df):

  ref_dates = cl_df['REF_DATE'].unique()
  geos = cl_df['GEO'].unique()
  my_array = []
  for ref_date in ref_dates:
    for geo in geos:
      cl_NSc_df = cl_df[(cl_df.GEO == geo) & (cl_df.REF_DATE== ref_date)]
      mean_rslt = cl_NSc_df["VALUE"].mean()
      my_array.append([geo, ref_date, mean_rslt])

  df = pd.DataFrame(my_array, columns = ['GEO','REF_DATE','VALUE'])
  return df 


# Function for the server
def create_server(data):
  
  def f(input, output, session):
    @output(id = "barplot")
    @render.plot
    def plot():
      req(input.geo_locations())
      req(input.secure_status())

      geo_location = list(input.geo_locations())
      food_secure_status = input.secure_status()
      food_sec_data = data.loc[data['Household food security status'] == food_secure_status]
      mean_data = generate_mean_of_data(food_sec_data)
      plot_data = mean_data[mean_data['GEO'].isin(geo_location)]
      plot = create_plot(plot_data)
      return plot
  return f

# Filter out empty data and pre process the data
df_0 = df.drop(columns=['SYMBOL', 'TERMINATED'])
df_1 = df_0.loc[df['Statistics'] == "Percentage of persons"]
#df_2 = df_1.loc[df['Household food security status'] == "Food insecure"]
df = df_1.dropna(subset=['VALUE'])
cl_df = df[['GEO', 'REF_DATE','Household food security status',  'VALUE' ]]

server = create_server(cl_df)
app = App(ui_obj, server)
