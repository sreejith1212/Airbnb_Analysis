# Airbnb Analysis
Building a simple user friendly UI with Streamlit, which can retrieve data from the MongoDB, perform data cleaning and preparation, do initial analysis and find relations between different data fields, display interactive geospatial visualizations, and create dynamic plots on the streamlit UI and Power BI dashboard to gain insights into pricing variations, availability patterns, and location-based trends.
## Pre-Requisite
1) Python: Install Python
2) MongoDB: Install MongoDB on your system.
3) Power BI Desktop App: Install Power BI Desktop App on your system.

## Installation
1) Clone the repo, create and activate the environment for the project.
2) Install all required packages from requirements.txt file using command: "pip install -r requirements.txt"

## Usage
1) To start the app, run command: "streamlit run airbnb_analysis.py"
2) From "Data Preparation" page, connect to MongoDB and retrieve the airbnb data. Also from this page, preprocess the extracted data.
3) From "Exploratory Data Analysis (EDA)" page, do basic EDA to analyse the extracted data.
4) From "Geospatial visualization" page, user can search different property types for the available countries with the option to filter out properties based on review score. These results are displayed on a map for easy identification of geographical position of the property.
5) From "Advanced Analysis" page, get general insights about the extracted airbnb data.
6) User can also view the power BI dashboard attached to the repository. 

## Features
1) Setting up Streamlit app: Using Streamlit application to create a simple UI.
2) MongoDB Connection and Data Retrieval: Setting up connection to MongoDB and retrieve the airbnb data.
3) Data Cleaning and Preparation: Using Pandas to preprocess the data (type conversion, managing missing values, etc).
4) Exploratory Data Analysis: Doing basic EDA to analyse the extracted data to get initial insights and finding out patterns from the data.
5) Geospatial Visualization: To view the airbnb listings available across multiple countries on a map for easy identification of geographical position of the property.
6) Advanced Analysis And Power BI Dashboard Creation: Plotted various charts and figures on the streamlit UI and Power BI dashboard to get detailed insights on the airbnb properties data.
