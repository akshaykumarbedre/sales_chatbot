import streamlit as st
import json
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory

# Load the saved data
def load_data():
    try:
        with open('sales_chatbot_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Save data to file
def save_data(data):
    with open('sales_chatbot_data.json', 'w') as f:
        json.dump(data, f, indent=2)

# Initialize ChatGroq LLM
llm = ChatGroq(model="llama-3.2-11b-vision-preview", api_key="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")

# Create a prompt template
system_template = """
You are a sales representative for the following product:
{product_info}

Your tone should be {tone} and you should communicate in {language}.

Here are some common objections and how to handle them:
{objections}

Here are some frequently asked questions and their answers:
{faqs}

Use the following sales script as a guideline:
{sales_script}

Provide the following links if the customer indicates they're ready to buy:
{links_info}

Remember to be helpful, professional, and always prioritize the customer's needs.
Your goal is to make the sale.
"""

human_template = """
Human: {human_input}
AI:"""

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])

# Create LLMChain with memory
memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
llm_chain = LLMChain(llm=llm, prompt=chat_prompt, memory=memory)

def generate_response(product_info, human_input, links_info, tone, language, objections, faqs, sales_script):
    try:
        response = llm_chain.invoke(input={
            'product_info': product_info,
            'human_input': human_input,
            'links_info': links_info,
            'tone': tone,
            'language': language,
            'objections': objections,
            'faqs': faqs,
            'sales_script': sales_script
        })
        return response['text']
    except Exception as e:
        st.error(f"An error occurred while generating the response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now. How else can I assist you?"

def format_product_info(data):
    product_info = f"""
    Product Name: {data.get('product_name', 'N/A')}
    Description: {data.get('product_description', 'N/A')}
    Pricing: {data.get('pricing_details', 'N/A')}
    """
    return product_info

def input_form():
    st.header("Sales Chatbot Input Form")

    data = load_data() or {}

    # Product/Service Information
    st.subheader("Product/Service Information")
    data['product_name'] = st.text_input("Product Name", value=data.get('product_name', ''))
    data['product_description'] = st.text_area("Product Description", value=data.get('product_description', ''))
    data['pricing_details'] = st.text_area("Pricing Details", value=data.get('pricing_details', ''))
    
    # FAQs
    st.subheader("FAQs")
    faq_count = st.number_input("Number of FAQs", min_value=1, value=len(data.get('faqs', [])) or 3)
    data['faqs'] = []
    for i in range(faq_count):
        question = st.text_input(f"FAQ Question {i+1}", value=data.get('faqs', [{}])[i].get('question', '') if i < len(data.get('faqs', [])) else '')
        answer = st.text_area(f"FAQ Answer {i+1}", value=data.get('faqs', [{}])[i].get('answer', '') if i < len(data.get('faqs', [])) else '')
        data['faqs'].append({"question": question, "answer": answer})

    # Sales Strategy and Approach
    st.subheader("Sales Strategy and Approach")
    data['sales_script'] = st.text_area("Sales Guidelines", value=data.get('sales_script', ''))
    data['tone'] = st.selectbox("Tone", ["Formal", "Casual", "Friendly"], index=["Formal", "Casual", "Friendly"].index(data.get('tone', 'Formal')))
    data['language'] = st.text_input("Language", value=data.get('language', ''))

    # Objection Handling
    st.subheader("Objection Handling")
    objection_count = st.number_input("Number of Objections", min_value=1, value=len(data.get('objections', [])) or 3)
    data['objections'] = []
    for i in range(objection_count):
        objection = st.text_input(f"Objection {i+1}", value=data.get('objections', [{}])[i].get('objection', '') if i < len(data.get('objections', [])) else '')
        response = st.text_area(f"Response {i+1}", value=data.get('objections', [{}])[i].get('response', '') if i < len(data.get('objections', [])) else '')
        data['objections'].append({"objection": objection, "response": response})

    # Actionable Links & Calls to Action
    st.subheader("Actionable Links & Calls to Action")
    data['purchase_link'] = st.text_input("Purchase Link", value=data.get('purchase_link', ''))
    data['product_demo_link'] = st.text_input("Product Demo Link", value=data.get('product_demo_link', ''))
    data['appointment_booking_link'] = st.text_input("Appointment Booking Link", value=data.get('appointment_booking_link', ''))

    if st.button("Save Data"):
        save_data(data)
        st.success("Data saved successfully!")

    return data

def chatbot(data):
    st.header("AI Sales Chatbot")

    # Format product info
    product_info = format_product_info(data)
    
    # Format other data
    objections = "\n".join([f"Objection: {obj.get('objection', 'N/A')}\nResponse: {obj.get('response', 'N/A')}" for obj in data.get('objections', [])])
    faqs = "\n".join([f"Q: {faq.get('question', 'N/A')}\nA: {faq.get('answer', 'N/A')}" for faq in data.get('faqs', [])])
    links_info = f"""
    Purchase Link: {data.get('purchase_link', 'Not available')}
    Product Demo Link: {data.get('product_demo_link', 'Not available')}
    Appointment Booking Link: {data.get('appointment_booking_link', 'Not available')}
    """

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "human", "content": user_input})
        
        # Display user message
        with st.chat_message("human"):
            st.markdown(user_input)

        # Generate AI response
        ai_response = generate_response(
            product_info=product_info,
            human_input=user_input,
            links_info=links_info,
            tone=data.get('tone', 'Neutral'),
            language=data.get('language', 'English'),
            objections=objections,
            faqs=faqs,
            sales_script=data.get('sales_script', 'No sales script provided.')
        )

        # Add AI response to chat history
        st.session_state.messages.append({"role": "ai", "content": ai_response})
        
        # Display AI response
        with st.chat_message("ai"):
            st.markdown(ai_response)

def main():
    st.title("Sales Chatbot Application")

    # Create tabs for Input Form and Chatbot
    tab1, tab2 = st.tabs(["Input Form", "Chatbot"])

    with tab1:
        data = input_form()

    with tab2:
        if data:
            chatbot(data)
        else:
            st.warning("Please fill out and save the input form before using the chatbot.")

if __name__ == "__main__":
    main()