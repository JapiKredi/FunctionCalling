from openai import OpenAI
import time

# yfinance module is a popular library that provides a convenient way to download historical market data from Yahoo Finance. 
# It allows you to fetch historical stock prices, financial statements, and other data related to publicly traded companies.
import yfinance as yf

# load_dotenv function is used to load the environment variables from the .env file into the current environment. 
# Once loaded, these environment variables can be accessed within the Python script using os.environ or other methods.
from dotenv import load_dotenv
import os
import json

# load_dotenv(), the code is instructing the dotenv module to read the .env file and set the environment variables defined in it. 
# Once loaded, these environment variables can be accessed within the Python script using os.environ or other methods.
load_dotenv()

# The following function is designed to fetch the latest closing price of a stock based on its symbol using the yfinance library.
# The get_stock_price function takes a symbol parameter of type str, representing the stock symbol, and returns a float value.
# Create a Ticker object from the yf module, using the symbol parameter. This object represents the stock with the specified symbol.
# Then, it retrieves the historical stock data for the last day (period="1d") using the history method of the Ticker object. 
# It specifically selects the 'Close' column of the data and retrieves the last value using .iloc[-1].

def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price

# Define a class called AssistantManager that manages an assistant for interacting with the OpenAI API.
# initializes the AssistantManager object with an api_key and an optional model parameter. 
# Set the api_key to the client attribute, sets the model to the model attribute, and initializes the assistant, thread, and run attributes to None.


class AssistantManager:
    def __init__(self, api_key, model="gpt-4-1106-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None

# Creating a class that manages an assistant, creates an assistant, creates a thread, and adds messages to the thread using the OpenAI API.
# The create_assistant method creates an assistant using the OpenAI API. 
# It takes name, instructions, and tools as parameters and assigns the created assistant to the assistant attribute.

    def create_assistant(self, name, instructions, tools):
        self.assistant = self.client.beta.assistants.create(
            name-name,
            instructions=instructions,
            tools=tools,
            model=self.model          
        )

# The create_thread method creates a thread using the OpenAI API.
# It assigns it to the thread attribute.

    def create_thread(self):
        self.thread = self.client.beta.threads.create()

# Add a message to the thread. 
# It takes role and content as parameters and creates a message in the thread using the OpenAI API.
    def add_message_to_thread(self,role,content):
        self.client.beta.threads.messages.create(
            threads_id = self.thread.id,
            role=role,
            content=content
        )
        
    # run_assistant method is a function that runs the assistant for a given set of instructions.
    # Creates a new run for the assistant using the beta.threads module of the client object. 
    # It takes instructions as a parameter and assigns the created run to the run attribute.
    # thread_id: The ID of the thread associated with the run, which is obtained from the self.thread attribute.
    # assistant_id: The ID of the assistant to be used for the run, which is obtained from the self.assistant attribute.
    # instructions: The instructions to be provided to the assistant during the run
    def run_assistant(self, instructions):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=instructions
        )

    # wait_for_completion method is a function that waits for the assistant to complete processing the run.
    def wait_for_completion(self):
        while True:
            time.sleep(5)
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=self.run.id
            )
            print(run_status.model_dump_json(indent=4))

            if run_status.status == 'completed':
                self.process_messages()
                break
            elif run_status.status == 'requires_action':
                print("Function Calling ...")
                self.call_required_functions(run_status.required_action.submit_tool_outputs.model_dump())
            else:
                print("Waiting for the Assistant to process...")

    def process_messages(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()}: {content}")

    def call_required_functions(self, required_actions):
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name == "get_stock_price":
                output = get_stock_price(symbol=arguments['symbol'])
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )


def main():
    api_key = os.getenv("api_key")
    manager = AssistantManager(api_key)
    # process 1
    manager.create_assistant(
        name="Data Analyst Assistant",
        instructions="You are a personal Data Analyst Assistant",
        tools=[{
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Retrieve the latest closing price of a stock using its ticker symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The ticker symbol of the stock"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        }]
    )
    # process 2
    manager.create_thread()
    # process 3
    manager.add_message_to_thread(role="user", content="Can you please provide me the stock price of Apple?")
    # process 4
    manager.run_assistant(instructions="Please address the user as Theophilus Siameh.")
    # final
    manager.wait_for_completion()


if __name__ == '__main__':
    main()