import streamlit as st
import json

def save_data(data):
    with open('sales_chatbot_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def main():
    st.title("Sales Chatbot Input Form")

    data = {}

    # Product/Service Information
    st.header("Product/Service Information")
    data['product_name'] = st.text_input("Product Name")
    data['product_description'] = st.text_area("Product Description")
    data['pricing_details'] = st.text_area("Pricing Details")
    
    # FAQs
    st.subheader("FAQs")
    faq_count = st.number_input("Number of FAQs", min_value=1, value=3)
    data['faqs'] = []
    for i in range(faq_count):
        question = st.text_input(f"FAQ Question {i+1}")
        answer = st.text_area(f"FAQ Answer {i+1}")
        data['faqs'].append({"question": question, "answer": answer})

    # Sales Strategy and Approach
    st.header("Sales Strategy and Approach")
    data['sales_script'] = st.text_area("Sales Guidelines")
    data['tone'] = st.selectbox("Tone", ["Formal", "Casual", "Friendly"])
    data['language'] = st.text_input("Language")


    # Actionable Links & Calls to Action
    st.header("Actionable Links & Calls to Action")
    data['purchase_link'] = st.text_input("Purchase Link")
    data['product_demo_link'] = st.text_input("Product Demo Link")
    data['appointment_booking_link'] = st.text_input("Appointment Booking Link")

    # Handling Customer Queries
    st.header("Handling Customer Queries")
    st.write("FAQs have already been covered in the Product/Service Information section.")
    st.write("Objection Handling has already been covered in the Sales Strategy and Approach section.")

    if st.button("Save Data"):
        save_data(data)
        st.success("Data saved successfully!")

if __name__ == "__main__":
    main()