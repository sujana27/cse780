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


import plotnine as gg
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
    ui.panel_title("Food-Status in Canada"),
    
    # Subtitle
    ui.markdown(
        """
        Data: [Food-waste](https://ansperformance.eu/data/)
        """
    ),
    ui.row(
        # line chart output
        ui.column(10, ui.output_plot("barplot")
        ), 
        # controls
        ui.column(2, 
          ui.markdown(
            """
            ### **Controls**
            Select provinces to explore.
            """
          ),
          ui.input_checkbox_group(
              "geo_locations", "Locations",
              choices=["Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta", "Newfoundland and Labrador", "Prince Edward Island", "British Columbia"],
              selected=["Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta", "Newfoundland and Labrador", "Prince Edward Island", "British Columbia"]
          )
        )
    ), ui.markdown(
        """
        Data: [Categorical value](https://ansperformance.eu/data/)
        """
    )
  )
  return app_ui

ui_obj = create_ui()


# Function to make the plot
def create_plot(data):
  plot = (
 
    gg.ggplot(data = data, mapping = gg.aes(x = 'REF_DATE', y='VALUE', fill='VALUE', group=data['GEO'])) +
      gg.theme_minimal() +
      gg.geom_line(linetype = "dotted")+
      gg.geom_point()+
      #gg.geom_line(aes(linetype=data['GEO']))+
      #gg.scale_linetype_manual(values=c("twodash", "dotted"))
      gg.labs(x = "Year", y = "Avg. Food Waste(%)", title="Food waste over the year") +
      gg.geom_point(aes(shape=data['GEO']))+
      gg.theme(panel_grid_major_x = gg.element_blank(), panel_grid_minor_x = gg.element_blank())
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
      geo_location = list(input.geo_locations())
      mean_data = generate_mean_of_data(data)
      plot_data = mean_data[mean_data['GEO'].isin(geo_location)]
      plot = create_plot(plot_data)
      return plot
  return f

# Filter out empty data and pre process the data
df_0 = df.drop(columns=['SYMBOL', 'TERMINATED'])
df_1 = df_0.loc[df['Statistics'] == "Percentage of persons"]
df_2 = df_1.loc[df['Household food security status'] == "Food insecure"]
df = df_2.dropna(subset=['VALUE'])
cl_df = df[['GEO', 'REF_DATE', 'VALUE']]

server = create_server(cl_df)
app = App(ui_obj, server)
