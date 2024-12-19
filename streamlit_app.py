import streamlit as st
import pandas as pd
import requests

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data from the Snowflake table
my_dataframe = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select('FRUIT_NAME', 'SEARCH_ON')

# Convert to pandas DataFrame for easy manipulation
pd_df = my_dataframe.to_pandas()

# Display the fruit options in a table
st.dataframe(pd_df)

# Input for "Name on Smoothie"
name_on_order = st.text_input("Name on Smoothie:")
st.write(f"The Name on your smoothie will be {name_on_order}")

# Ingredient selection (allowing up to 5 fruits)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # List of fruit names
    max_selections=5
)

# When ingredients are selected
if ingredients_list:
    st.write("You selected these ingredients:")
    st.write(ingredients_list)

    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '  # Build the ingredients string

        # Get the 'SEARCH_ON' value for each selected fruit from the DataFrame
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Display nutrition information for each selected fruit
        st.subheader(f'{fruit_chosen} Nutrition Information')

        # Assuming the API URL for nutrition data (adjust this as needed)
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        # If the API call is successful, display the results
        if smoothiefroot_response.status_code == 200:
            sf_data = smoothiefroot_response.json()  # Get the JSON response
            st.json(sf_data)  # Show the nutrition info in a readable format
        else:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}")

    # Insert the order into Snowflake when the button is pressed
    my_insert_stmt = f""" 
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER) 
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Button to submit the order
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            # Execute the SQL statement to insert the order
            session.sql(my_insert_stmt).collect()
            st.success('Your smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")
