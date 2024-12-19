# Import python packages
import streamlit as st
import requests
import pandas


from snowflake.snowpark.functions import col


# Write directly to the app
st.title("Example Streamlit App :balloon:")
st.write(
    """Replace this example with your own code!
    **And if you're new to Streamlit,** check
    out our easy-to-follow guides at
    [docs.streamlit.io](https://docs.streamlit.io).
    """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your smoothie will be ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width = True)
#st.stop()

pd_df=my_dataframe.to_pandas()
st.data_frame(pd_df)
st.stop

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)

    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    st.write(ingredients_string)


    my_insert_stmt = """ insert into SMOOTHIES.PUBLIC.ORDERS(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


