from pymongo import MongoClient
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

def preprocess_airbnb_data(airbnb_data):

    try:
        # converting to required datatype
        airbnb_data['Maximum_nights'] = airbnb_data['Maximum_nights'].astype(int)
        airbnb_data['Minimum_nights'] = airbnb_data['Minimum_nights'].astype(int)
        airbnb_data['Security_deposit'] = airbnb_data['Security_deposit'].astype(str)
        airbnb_data['Security_deposit'] = pd.to_numeric(airbnb_data['Security_deposit'], errors="coerce")
        airbnb_data['Price'] = airbnb_data['Price'].astype(str)
        airbnb_data['Price'] = airbnb_data['Price'].astype(float)
        airbnb_data['Cleaning_fee'] = airbnb_data['Cleaning_fee'].astype(str)
        airbnb_data['Cleaning_fee'] = pd.to_numeric(airbnb_data['Cleaning_fee'], errors="coerce")
        airbnb_data['Extra_people'] = airbnb_data['Extra_people'].astype(str)
        airbnb_data['Extra_people'] = airbnb_data['Extra_people'].astype(float)
        airbnb_data['Extra_people'] = airbnb_data['Extra_people'].astype(int)
        airbnb_data['Guests_included'] = airbnb_data['Guests_included'].astype(str)
        airbnb_data['Guests_included'] = airbnb_data['Guests_included'].astype(float)
        airbnb_data['Guests_included'] = airbnb_data['Guests_included'].astype(int)
        # updating empty values with relevant data
        airbnb_data['Total_beds'] = airbnb_data['Total_beds'].fillna(airbnb_data['Total_beds'].value_counts().idxmax())
        airbnb_data['Total_bedrooms']= airbnb_data['Total_bedrooms'].fillna(airbnb_data['Total_bedrooms'].value_counts().idxmax())
        airbnb_data['Security_deposit'] = airbnb_data['Security_deposit'].fillna(int(airbnb_data['Security_deposit'].mean()))
        airbnb_data['Cleaning_fee'] = airbnb_data['Cleaning_fee'].fillna(airbnb_data['Cleaning_fee'].mean())
        airbnb_data['Review_scores'] = airbnb_data['Review_scores'].fillna(airbnb_data['Review_scores'].value_counts().idxmax())

        airbnb_data['Description'] = airbnb_data['Description'].replace(to_replace='', value='NA')
        airbnb_data['House_rules'] = airbnb_data['House_rules'].replace(to_replace='', value='NA')
        airbnb_data['Amenities'] = airbnb_data['Amenities'].replace(to_replace='', value='NA')
        return airbnb_data
      
    except Exception as e:
        st.error(f"Error in preprocessing data : {e}")

def filter_processed_airbnb_df(processed_airbnb_df):


    country_mean_price = processed_airbnb_df.groupby(processed_airbnb_df["Country"]).agg({'Price': 'mean'}).reset_index()
    property_mean_price = processed_airbnb_df.groupby([processed_airbnb_df["Country"], processed_airbnb_df["Property_type"]]).agg({'Price': 'mean'}).reset_index()
    country_availability_mean = processed_airbnb_df.groupby([processed_airbnb_df["Country"], processed_airbnb_df["Property_type"]]).agg({'Availability_365': 'mean'}).reset_index() 
    room_type_property_mean_price = processed_airbnb_df.groupby([processed_airbnb_df["Country"], processed_airbnb_df["Property_type"], processed_airbnb_df["Room_type"]]).agg({'Price': 'mean'}).reset_index()
    hotel_count_by_property = processed_airbnb_df.groupby([processed_airbnb_df["Country"], processed_airbnb_df["Property_type"]]).size().reset_index(name='count')

    #most preferred by property type
    preferred_property_country = processed_airbnb_df[processed_airbnb_df["Number_of_reviews"] >= 100]
    preferred_property_country = preferred_property_country.groupby([processed_airbnb_df["Country"], processed_airbnb_df["Property_type"]]).agg({"Review_scores": "mean"}).reset_index()
    idx = preferred_property_country.groupby('Country')['Review_scores'].idxmax()
    preferred_property_country = preferred_property_country.loc[idx]

    return country_mean_price, property_mean_price, country_availability_mean, room_type_property_mean_price, hotel_count_by_property, preferred_property_country


if __name__ == "__main__":

    #Initializing the session state
    if 'airbnb_data' not in st.session_state:
        st.session_state.airbnb_data = None
    if 'processed_airbnb_df' not in st.session_state:
        st.session_state['processed_airbnb_df'] = None

    # set app page layout type
    st.set_page_config(layout="wide")

    # create sidebar
    with st.sidebar:        
        page = option_menu(
                            menu_title='Airbnb Analysis',
                            options=['Data Preparation','Exploratory Data Analysis (EDA)', 'Geospatial Visualization', 'Advanced Analysis'],
                            icons=['gear', 'map', 'info-circle', 'bar-chart-line'],
                            menu_icon="pin-map-fill",
                            default_index=0 ,
                            styles={"container": {"padding": "5!important"},
                                    "icon": {"color": "brown", "font-size": "23px"}, 
                                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "lightblue", "display": "flex", 
                                                 "align-items": "center"},
                                    "nav-link-selected": {"background-color": "grey"},}  
        )


if page == "Data Preparation":

    st.header("Airbnb Data Retrieval and Data Preprocessing", divider = "rainbow")
    st.write("")
    col1, col2 = st.columns([1,1])
    container_1 = col1.container(border=False, height=550)
    container_2 = col2.container(border=False, height=550)
    airbnb_data_extract = container_1.button("Connect to MongoDB", use_container_width = True)
    container_1.image("data_image.webp")
    data = []
    if airbnb_data_extract:
        #Connecting to MongoDB
        client = MongoClient("mongodb://localhost:27017")
        #Accessing airbnb data
        db = client["sample_airbnb"]
        collection = db["listingsAndReviews"]

        extracted_data = collection.find()
        airbnb_required_data = []
        # a = 0
        for data in extracted_data:
            dict_data = dict(Id = data['_id'],
                             Listing_url = data['listing_url'],
                             Name = data.get('name'),
                             Description = data['description'],
                             House_rules = data.get('house_rules'),
                             Property_type = data['property_type'],
                             Room_type = data['room_type'],
                             Bed_type = data['bed_type'],
                             Minimum_nights = int(data['minimum_nights']),
                             Maximum_nights = int(data['maximum_nights']),
                             Cancellation_policy = data['cancellation_policy'],
                             Accommodates = data['accommodates'],
                             Total_bedrooms = data.get('bedrooms'),
                             Total_beds = data.get('beds'),
                             Number_of_reviews = data['number_of_reviews'],
                             Amenities = ', '.join(data['amenities']),
                             Price = data['price'],
                             Security_deposit = data.get('security_deposit'),
                             Cleaning_fee = data.get('cleaning_fee'),
                             Extra_people = data['extra_people'],
                             Guests_included= data['guests_included'],
                             Host_id = data['host']['host_id'],
                             Host_name = data['host']['host_name'],
                             Street = data['address']['street'],
                             Country = data['address']['country'],
                             Country_code = data['address']['country_code'],
                             Location_type = data['address']['location']['type'],
                             Longitude = data['address']['location']['coordinates'][0],
                             Latitude = data['address']['location']['coordinates'][1],
                             Is_location_exact = data['address']['location']['is_location_exact'],
                             Availability_365 = data['availability']['availability_365'],
                             Review_scores = data['review_scores'].get('review_scores_rating')     
            )
            airbnb_required_data.append(dict_data)
            # a += 1
            # if a == 100:
            #     break

        st.session_state.airbnb_data = pd.DataFrame(airbnb_required_data)
        if st.session_state.airbnb_data is not None:
            container_2.success("The data has been fetched successfully!")
            container_2.dataframe(st.session_state.airbnb_data, use_container_width=True)
        else:
            container_2.error("Error in data preparation")

    airbnb_data = st.session_state.airbnb_data
    col3, col4 = st.columns([1,1])
    preprocess_button = col3.button("Click to preprocess extracted data", use_container_width = True)
    if preprocess_button:
        if airbnb_data is not None:
                processed_df = preprocess_airbnb_data(airbnb_data)
                # Storing processed data in session state
                st.session_state['processed_airbnb_df'] = processed_df
                if processed_df is not None:
                    container_2.success("Successfully cleaned and preprocessed data")
                container_2.dataframe(st.session_state['processed_airbnb_df'])
        else:
            container_2.warning("Please fetch data first!")


if page == "Exploratory Data Analysis (EDA)":
    
    processed_airbnb_df = st.session_state['processed_airbnb_df']
    
    st.header("Exploratory Data Analysis (EDA) on Preprocessed Airbnb Data", divider = "rainbow")

    # Distribution Plots
    with st.expander("1) Distribution Plots"):
        
        col01, col02 = st.columns([1,1])
        container_0 = col01.container(border=True)
        st.write("")
        cols_in_grid = container_0.slider(':blue[Number of columns in the grid]', 1, 4, 2)
        if processed_airbnb_df is not None:
            # histograms
            st.subheader("Histograms")
            histo_columns = ['Minimum_nights', 'Maximum_nights', 'Accommodates', 'Total_bedrooms', 'Total_beds', 'Number_of_reviews', 
                                'Price', 'Security_deposit', 'Cleaning_fee', 'Extra_people', 'Guests_included', 'Availability_365', 'Review_scores']
            
            req_columns = len(histo_columns)
            rows_in_grid = (req_columns + cols_in_grid - 1) // cols_in_grid

            fig, axes = plt.subplots(rows_in_grid, cols_in_grid, figsize=(15, 5 * rows_in_grid))
            axes = axes.flatten()
            for i, column in enumerate(histo_columns):
                sns.histplot(processed_airbnb_df[column], kde=True, bins=20, ax=axes[i])
                axes[i].set_title(column)
                axes[i].set_ylabel('Frequency')

            for j in range(req_columns, len(axes)):
                fig.delaxes(axes[j])

            plt.tight_layout()
            st.pyplot(fig)

            # box plots
            st.subheader("Box Plots")
            boxplt_columns = ['Minimum_nights', 'Maximum_nights', 'Accommodates', 'Total_bedrooms', 'Total_beds', 'Availability_365', 
                                'Price', 'Security_deposit', 'Cleaning_fee', 'Extra_people', 'Review_scores']
            
            req_columns = len(boxplt_columns)
            rows_in_grid = (req_columns + cols_in_grid - 1) // cols_in_grid

            fig, axes = plt.subplots(rows_in_grid, cols_in_grid, figsize=(15, 5 * rows_in_grid))
            axes = axes.flatten()
            
            for i, column in enumerate(boxplt_columns):
                sns.boxplot(data = processed_airbnb_df[column], ax=axes[i])
                axes[i].set_title(column)

            for j in range(req_columns, len(axes)):
                fig.delaxes(axes[j])

            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.warning("Processed Data Not Available!")

    # Relationship Plots
    with st.expander("2) Relationship Plots"):

        if processed_airbnb_df is not None:
            # scatter plots
            st.subheader("Scatter Plots")
            fig, axes = plt.subplots(3, 2, figsize=(15, 15))

            sns.scatterplot(x='Review_scores', y='Price', data=processed_airbnb_df, ax=axes[0, 0])
            axes[0, 0].set_title('Review Scores Vs Price')

            sns.scatterplot(x='Accommodates', y='Price', data=processed_airbnb_df, ax=axes[0, 1])
            axes[0, 1].set_title('Accommodates Vs Price')

            sns.scatterplot(x='Availability_365', y='Price', data=processed_airbnb_df, ax=axes[1, 0])
            axes[1, 0].set_title('Availability_365 Vs Price')

            sns.scatterplot(x='Property_type', y='Price', data=processed_airbnb_df, ax=axes[1, 1])
            axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=90)
            axes[1, 1].set_title('Property Type Vs Price')

            sns.scatterplot(x='Number_of_reviews', y='Price', size='Accommodates', data=processed_airbnb_df, ax=axes[2, 0])
            axes[2, 0].set_title('Number of Reviews Vs Price')


            price_review = sns.scatterplot(x='Price', y='Review_scores', hue='Property_type', data=processed_airbnb_df, ax=axes[2, 1])
            axes[2, 1].set_title('Price vs. Review Scores (Upon Property Type)')
            price_review.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.warning("Processed Data Not Available!")

    # Categorical Plots
    with st.expander("3) Categorical Plots"):

        if processed_airbnb_df is not None:
            
            st.subheader("Count Plots")   
            fig, ax = plt.subplots(figsize=(12, 3))
            sorted_property_types = processed_airbnb_df['Country'].value_counts()
            ax = sns.countplot(data=processed_airbnb_df, x='Country', order=sorted_property_types.index, palette="Paired", ax=ax)
            ax.set_title("Count for each country")
            st.pyplot(fig)

            fig, ax = plt.subplots(figsize=(12, 5))
            sorted_property_types = processed_airbnb_df['Property_type'].value_counts()
            ax = sns.countplot(data=processed_airbnb_df, y='Property_type', order=sorted_property_types.index, palette="Set2", ax=ax)
            ax.set_title("Count for each property type")
            st.pyplot(fig)


            fig, ax = plt.subplots(figsize=(12, 2))
            ax = sns.countplot(data=processed_airbnb_df, y='Room_type', palette='Dark2')
            ax.set_title("Count of each room type")
            st.pyplot(fig)

            fig, ax = plt.subplots(figsize=(12, 2))
            ax = sns.countplot(data=processed_airbnb_df, x='Cancellation_policy', palette='pastel')
            ax.set_title("Count of each Cancellation policy")
            st.pyplot(fig)

            fig, ax = plt.subplots(figsize=(12, 3))
            ax = sns.countplot(data=processed_airbnb_df, x='Bed_type', palette='Accent')
            ax.set_title("Count of each bed type")
            st.pyplot(fig)

        else:
            st.warning("Processed Data Not Available!")

    #Heatmap
    with st.expander("4) Heatmap"):

        if processed_airbnb_df is not None:
            st.subheader("Heatmap")
            heatmp_columns = ['Minimum_nights', 'Maximum_nights', 'Accommodates', 'Total_bedrooms', 'Total_beds', 'Availability_365', 'Number_of_reviews',
                                'Price', 'Security_deposit', 'Cleaning_fee', 'Extra_people', 'Guests_included',  'Review_scores']
            req_columns = processed_airbnb_df[heatmp_columns]
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(req_columns.corr(), annot=True, cmap='viridis', vmin=-1, vmax=1, ax=ax)
            plt.title('Correlation Heatmap')
            st.pyplot(plt)

        else:
            st.warning("Processed Data Not Available!")

if page == "Geospatial Visualization":

    processed_airbnb_df = st.session_state['processed_airbnb_df']
    st.header("Search Airbnb with Geospatial Visualization", divider = "rainbow")
    if processed_airbnb_df is not None:
        st.write("")
        col5, col6 = st.columns([2,3])
        col5.write("")
        col5.write("")
        col5.write("")
        col5.write("")
        country = col5.selectbox('Select Country',sorted(processed_airbnb_df.Country.unique()), index=None, placeholder="Country")
        col5.write("")
        property_type = col5.selectbox('Select Property_type',sorted(processed_airbnb_df.Property_type.unique()), index=None, placeholder="Property Type")
        col5.write("")
        ratings = col5.slider("Select Rating range:", min_value = 0, max_value = 100, value = (0, 10), step=1)
        minimum_price = processed_airbnb_df.Price.min()
        maximum_price = processed_airbnb_df.Price.max()
        col5.write("")
        price_range = col5.slider('Select Price Range', min_value = minimum_price, max_value = maximum_price, value = (minimum_price, maximum_price), step=1.0)
        col5.write("")

        if country is not None and property_type is not None:
            filter_result_query = (f'Country == "{country}" & Property_type == "{property_type}" & Price >= {price_range[0]} & Price <= {price_range[1]}'
                                f' & Review_scores >= {ratings[0]} & Review_scores <= {ratings[1]}')
            country_df = processed_airbnb_df.query(filter_result_query).groupby(['Country'],as_index=False)['Name'].count().rename(columns={'Name' : 'Total_Listings'})
            fig = px.choropleth(country_df,
                                featureidkey='properties.ST_NM',
                                locations='Country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale='Blues',
                                width=800,
                                height=600
                                )
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},geo=dict(bgcolor='#002b2b'),height=500, width=1300)
            container_3 = col6.container(border=True)
            container_3.subheader("Total Listings in each Country")
            container_3.plotly_chart(fig,use_container_width=True)
            
            col7, col8 = st.columns([2,3])
            container_4 = col7.container(height= 800, border=False)
            df = processed_airbnb_df.query(filter_result_query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False).head(5)
            fig = px.pie(df,
                            title='Hosts with highest Listings',
                            values='Listings', 
                            names='Host_name',
                            hover_data=['Listings'],
                            hole=0.5, 
                            height=400, 
                            width=650)
            fig.update_layout(showlegend=True)
            container_4.plotly_chart(fig, use_container_width=True)

            country_df = processed_airbnb_df[(processed_airbnb_df["Country"] == country) & (processed_airbnb_df["Property_type"] == property_type) & 
                                            (processed_airbnb_df["Price"] >= price_range[0]) & (processed_airbnb_df["Price"] <= price_range[1]) & 
                                            (processed_airbnb_df["Review_scores"] >= ratings[0]) & (processed_airbnb_df["Review_scores"] <= ratings[1])]

            names = country_df['Name'].values
            reviews = country_df['Number_of_reviews'].values
            ratings = country_df['Review_scores'].values
            price = country_df['Price'].values
            bedrooms = country_df['Total_bedrooms'].values
            room_type = country_df['Room_type'].values
            accommodates = country_df['Accommodates'].values
            security_deposit = country_df['Security_deposit'].values
            host_name = country_df['Host_name'].values
            latitudes = country_df['Latitude'].values
            longitudes = country_df['Longitude'].values

            container_5 = col8.container(border=True)
            if len(latitudes) != 0:
                with container_5:
                    st.subheader("View Airbnb on Map")
                    # Set initial location and zoom level
                    initial_location = [latitudes[0], longitudes[0]]
                    zoom_level = 1

                    # Create the Folium map
                    folium_map = folium.Map(
                    location=initial_location,
                    zoom_start=zoom_level,
                    tiles='CartoDB Voyager',
                    control_scale=True
                    )

                    # Adding a marker cluster
                    marker_cluster = MarkerCluster().add_to(folium_map)

                    # Add markers to the map
                    for i in range(len(names)):

                        popup_content = (f'<b>{names[i]}</b><br>'
                                        f'Host Name: {host_name[i]}<br>'
                                        f'Price: ${price[i]}<br>'
                                        f'Number of Reviews: {reviews[i]}<br>'
                                        f'Rating: {ratings[i]}<br>'
                                        f'Bedrooms: {bedrooms[i]}<br>'
                                        f'Room Type: {room_type[i]}<br>'
                                        f'Accommodates: {accommodates[i]}<br>'
                                        f'Security Deposit: ${security_deposit[i]}')
                        popup = folium.Popup(popup_content, max_width=300)

                        folium.Marker(
                            location=[latitudes[i], longitudes[i]],
                            popup=popup,
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(marker_cluster)
                
                    st_folium(folium_map, use_container_width=True)
    else:
        st.warning("Processed Data Not Available!")


if page == "Advanced Analysis":

    processed_airbnb_df = st.session_state['processed_airbnb_df']
    st.header("Advanced Analysis of the Airbnb Data", divider = "rainbow")
    if processed_airbnb_df is not None:

        country_mean_price, property_mean_price, country_availability_mean, room_type_property_mean_price, hotel_count_by_property, preferred_property_country = filter_processed_airbnb_df(processed_airbnb_df)

        container_6 = st.container(border=True)
        col9, col10 = container_6.columns([1,1])
        fig = px.pie(country_mean_price, 
                     values="Price", 
                     names="Country", 
                     hover_data=["Price"], 
                     hole=0.4, 
                     height=400, 
                     width=650,
                     title = "Average Airbnb Price For Each Country")
        col9.plotly_chart(fig)

        fig = px.scatter(country_availability_mean, 
                    x="Country", 
                    y="Availability_365", 
                    hover_data=["Availability_365"], 
                    color="Property_type", 
                    color_continuous_scale="temps", 
                    height=400, 
                    width=650,
                    title = "Average Availability For Each Property Type")
        col9.plotly_chart(fig)
        
        fig = px.bar(room_type_property_mean_price, 
                    x="Country", 
                    y="Price", 
                    color="Property_type", 
                    facet_col="Room_type", 
                    hover_data=["Price"], 
                    height=400, 
                    width=800,
                    title = "Average Airbnb Price For Each Room Type Across Each Property Type")
        col9.plotly_chart(fig) 

        fig = px.line(hotel_count_by_property, 
                    x="Country", 
                    y="count", 
                    color="Property_type", 
                    hover_data=["count"], 
                    height=400, 
                    width=800,
                    title = "Total Count for Each Property Type")
        col10.plotly_chart(fig) 

        fig = px.bar(preferred_property_country, 
                    x="Country", 
                    y="Review_scores", 
                    color="Property_type", 
                    hover_data=["Review_scores"], 
                    height=400, 
                    width=800,
                    title = "Most Preferred Property Types Across Each Country")
        col10.plotly_chart(fig)

        fig = px.scatter(property_mean_price, 
            x="Country", 
            y="Price", 
            hover_data=["Price"], 
            color="Property_type", 
            color_continuous_scale="temps", 
            height=400, 
            width=650,
            title = "Average Price For Each Property Type")
        col10.plotly_chart(fig)

    else:
        st.warning("Processed Data Not Available!")