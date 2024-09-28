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
        st.error("No data file found. Please run the input app first to create the data.")
        return None

# Initialize ChatGroq LLM
llm = ChatGroq(model="llama-3.2-11b-vision-preview", api_key="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")

# Create a prompt template
system_template = """
You are an  sales representative for the following product:
{product_info}

Your tone should be {tone} and you should communicate in {language}.

Here are some common objections and how to handle them:
{objections}

Here are some frequently asked questions and their answers:
{faqs}

Use the following sales script as a guideline:
{sales_script}

  provide the following links if indicates they're ready to buy and display the link:
{links_info}

Remember to be helpful, professional, and always prioritize the customer's needs.
you goal is to make the sale 
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
    Pricing:
    """
    pricing_details = data.get('pricing_details', 'N/A')
    
    if isinstance(pricing_details, dict):
        for item, price in pricing_details.items():
            product_info += f"    - {item}: ${price}\n"
    elif isinstance(pricing_details, list):
        for item in pricing_details:
            product_info += f"    - {item}\n"
    else:
        product_info += f"    {pricing_details}\n"
    
    return product_info

def main():
    st.title("AI Sales Chatbot")

    # Load the product data
    data = load_data()
    if not data:
        return

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

    print(links_info)
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

if __name__ == "__main__":
    main()