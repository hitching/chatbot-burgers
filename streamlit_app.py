import streamlit as st
from openai import OpenAI
import json

# Show title and description.
st.title("💬 How Did We Go With The Burgers?")
st.subheader("Tell us like it is. Win prizes for honesty.")
st.write(
    "We know we still have lots to learn about how we can do this delivery thing better. "
    "Please help us understand what we’re doing well and what we need to improve. "
    "This is an AI you’re talking to, so don’t be shy, don’t drop any punches, swear all you want. "
    "We really do want to hear everything you have to say, and we want to get better. "
)

openai_api_key = st.secrets["openai_key"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")

else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            try:
                content = json.loads(message["content"])
                st.markdown(content["response"])

            except Exception as err:
                st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        system_message = """You are a customer success manager at a McDonald’s restaurant, chatting to a customer who received a delivery of fast food and is providing feedback on how it went. 
Instructions: categorize the initial customer sentiment as “positive”, “neutral” or “negative”, and the change in customer sentiment as “no change”, “better”, or “worse”. 
Also categorize the root cause as either “delivery” (e.g. food was late, or food was cold, or the drinks had spilt) or “order” (e.g. something was missing from the order) or “unknown”. 
Also respond to the customer. 
If initial sentiment is “negative” or change in sentiment is “worse”, and the root cause is unknown, ask the customer questions that allow you to categorised the problem as “food”, or “delivery”. 

If initial sentiment is “negative” or change in sentiment is “worse” and the root cause is known, either:
* ask the customer what can be done to remedy the situation, or
* ask the customer if they might upload a photo showing the problem.

If initial sentiment is “positive” or the change in sentiment is “better”, either:
* respond showing ascii art of the team making the food, or the team delivering the food, or
* thank the customer for the feedback and suggest they write a 5-star review.
* invite the customer to provide their email address to be entered into a prize draw competition.

Try all of these things once.

If the customer has indicated that a voucher would remedy the situation, 
ask them to visit https://customerservices.mcdonalds.co.uk if the root cause is "order",
or https://help.uber.com/ubereats if the root cause is "delivery".
And ask if the customer has any positive feedback about the delivery?

Or otherwise respond to the customer in an empathetic and understanding tone.
If initial sentiment is “positive” or the change in sentiment is “better”, add some humour.
Try to make reference to local landmarks and street names and events. For example, "NW10", “Neasdon Lane”, “the North Circular”.
Answer in JSON format with keys “initial_sentiment”, “change_in_sentiment”, “root_cause” and “response”, for example {“initial_sentiment”:”negative”, “change_in_sentiment”:”better”, “root_cause”:“unknown”, “response”:”was the food okay?”}
"""

        messages = [{"role": "system", "content": system_message}]
        
        # hided excluded parts
        for message in st.session_state.messages:

            try:
                content = json.loads(message["content"])
                messages.append({"role": message["role"], "content": content["response"]})

            except Exception as err:
                messages.append({"role": message["role"], "content": message["content"]})
        
        # Generate a response using the OpenAI API.
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            #stream=True,
        )
        response_dict = ai_response.model_dump()
        message_content = response_dict["choices"][0]["message"]["content"]

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "assistant", "content": message_content})

        with st.chat_message("assistant"):
            try:
                content = json.loads(message_content)
                st.markdown(content["response"])

            except Exception as err:
                st.markdown(message_content)
