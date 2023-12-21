# Dependencies
# !pip install scipy
# !pip install tenacity
# !pip install tiktoken
# !pip install termcolor 
# !pip install openai
# !pip install requests

import json
import openai
import os
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from dotenv import load_dotenv

GPT_MODEL = "gpt-3.5-turbo-0613"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# the @retry decorator is being used to retry the decorated function in case of failures or exceptions. 
# It provides a way to automatically retry the function multiple times with a delay between each retry.
# The wait parameter specifies the wait strategy to use between retries.
# Delay between retries will be a random exponential backoff with a multiplier of 1 and a maximum delay of 40 seconds.
# The function will be retried for a maximum of 3 attempts. 
# If the function still fails after 3 attempts, the exception will be raised.
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))

# The chat_completion_request function is a Python function that sends a chat completion request to the OpenAI API. 
# It takes several parameters:
# 1: messages: A list of messages representing the conversation history. Each message in the list is a dictionary with a role (either "system", "user", or "assistant") and content (the text of the message).
# 2: tools: A list of tools to use in the assistant. Each tool is a dictionary with a name and description.
# 3: tool_choice: The name of the tool to use in the assistant.
# 4: model: The name of the model to use for the chat completion request.
# The function returns a response object from the OpenAI API.
# The response object contains the following attributes:
# 1: id: The ID of the chat completion request.
# 2: object: The type of object returned by the API.
# 3: created: The date and time the chat completion request was created.
# 4: model: The name of the model used for the chat completion request.
# 5: choices: A list of choices returned by the chat completion request. Each choice is a dictionary with a text attribute containing the text of the message.
# 6: created: The date and time the chat completion request was created.
# 7: model: The name of the model used for the chat completion request.

# Hereby the steps taken by the function
# 1: Inside the function, it prepares the necessary headers for the API request, including the content type and authorization using the OpenAI API key.
# 2: It then creates a JSON payload (json_data) containing the model, messages, and optional tools and tool choice.
# The function makes a POST request to the OpenAI API endpoint https://api.openai.com/v1/chat/completions with the headers and JSON payload. 
# It expects to receive a response from the API.
# f the request is successful, the function returns the response. 
# If an exception occurs during the request, it prints an error message and returns the exception object.

def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

# This function visually displays a conversation by printing each message with its role and content in a specific color, making it easier to distinguish between different roles in the conversation.
# The pretty_print_conversation function takes a list of messages as input and prints each message in a formatted way, assigning different colors to different roles in the conversation.
# Defines a dictionary role_to_color that maps each role ("system", "user", "assistant", "tool") to a corresponding color ("red", "green", "blue", "magenta").
# Iterates over each message in the messages list. For example: If the role of the message is "system", it prints the message with the prefix "system:" in the corresponding color.
# If the role of the message is "assistant" and the message has a key "function_call", it prints the message with the prefix "assistant:" and the value of the "function_call" key in the corresponding color.

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


# Defines a list of two tools, each represented as a dictionary. 
# These tools are both used for weather-related functionality.
# The first tool is a function that returns the current weather for a given location.
# The second tool is a function that returns the weather forecast for a given location for a given number of days.
# The tools list is passed as an argument to the chat_completion_request function.
# The chat_completion_request function makes a POST request to the OpenAI API endpoint https://api.openai.com/v1/chat/completions with the headers and JSON payload.
# It expects to receive a response from the API.
# If the request is successful, the function returns the response.

# The first tool consists of the following properties:
# 1: type: The type of tool. In this case, the type is "function".
# 2: function: A dictionary containing the name, description, and parameters of the function.
# 3: name: The name of the function.
# 4: description: A description of the function.
# 5: parameters: A dictionary containing the parameters of the function.
# 5a: type: The type of parameter. In this case, the type is "object".
# 5b: properties: A dictionary containing the properties of the parameter.
# 5b1: "location: A dictionary containing the type and description of the location parameter.
# 5b2: "format": A string parameter representing the temperature unit to use, with possible values of "celsius" or "fahrenheit". It is inferred from the user's location.
# 5c: required: A list of required parameters. In this case, the required parameters are "location" and "format".
# The second tool also consists of the property 'num_days': The number of days to forecas

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]


messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "What's the weather like today. I am in Glascow Scotland"})
chat_response = chat_completion_request(
    messages, tools=tools
)
assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "what is the weather going to be like in Glasgow, Scotland over the next x days"})
chat_response = chat_completion_request(
    messages, tools=tools
)
assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)

messages.append({"role": "user", "content": "5 days"})
chat_response = chat_completion_request(
    messages, tools=tools
)
chat_response.json()["choices"][0]

print(assistant_message)
pretty_print_conversation(messages)



# In the following code we are forcing the model to use the get_n_day_weather_forecast function by specifying the tool_choice parameter in the chat_completion_request function.
messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Give me a weather report for Toronto, Canada."})
chat_response = chat_completion_request(
    messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_n_day_weather_forecast"}}
)

assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)


# In the following code we NOT are forcing the model to use the get_n_day_weather_forecast function by specifying the tool_choice parameter in the chat_completion_request function.

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Give me a weather report for Toronto, Canada."})
chat_response = chat_completion_request(
    messages, tools=tools
)

assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)



messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Give me the current weather (use Celcius) for Toronto, Canada."})
chat_response = chat_completion_request(
    messages, tools=tools, tool_choice="none"
)

assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)
print(assistant_message)
pretty_print_conversation(messages)



# Paralell Function calling. GPT3.5 turno and GPT4 can call multiple functions at the same time. 

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "what is the weather going to be like in San Francisco and Glasgow over the next 4 days"})
chat_response = chat_completion_request(
    messages, tools=tools, model='gpt-3.5-turbo-1106'
)

chat_response.json()
assistant_message = chat_response.json()["choices"][0]["message"]['tool_calls']
messages.append(assistant_message)
print(assistant_message)

# imports the sqlite3 module, which is a built-in module in Python for working with SQLite databases.
import sqlite3

# establishes a connection to an SQLite database file named "Chinook.db" using the connect() function from the sqlite3 module. 
# The connect() function takes the database file path as an argument and returns a connection object (conn) that represents the connection to the database.
# Once the connection is established, you can use the conn object to execute SQL queries, fetch data, and perform other database operations.
conn = sqlite3.connect("data/Chinook.db")

print("Opened database successfully")

# This function provides a convenient way to retrieve the names of tables in an SQLite database using a given connection object.
# The get_table_names function takes a connection object conn as input and returns a list of table names present in the SQLite database.
# get_table_names that takes a single parameter conn, which represents the connection object to the SQLite database.
# Initializes an empty list table_names to store the table names.
# It executes an SQL query using the execute method of the conn object. The query selects the name column from the sqlite_master table where the type is 'table'. This query retrieves the names of all tables in the database.
# The function iterates over the result of the query using a for loop and the fetchall method. Each iteration retrieves a row from the result.
# Inside the loop, it appends the first element of each row (the table name) to the table_names list.
# After iterating over all rows, the function returns the table_names list containing the names of all tables in the database.

def get_table_names(conn):
    """Return a list of table names."""
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names

# This function provides a convenient way to retrieve the column names of a table in an SQLite database using a given connection object and table name.
# The get_column_names function takes two parameters, conn and table_name, and returns a list of column names for a given table in an SQLite database.
# Create an emmpty list of column names
# It executes an SQL query using the execute method of the conn object. The query uses the PRAGMA table_info statement to retrieve information about the columns of the specified table. The table_info pragma returns one row for each column in the table.
# The fetchall method is called on the result of the query to retrieve all rows returned by the query.
# The function iterates over the rows returned by the query using a for loop. Each iteration represents a column in the table.
# Inside the loop, it appends the second element of each row (the column name) to the column_names list.
# After iterating over all rows, the function returns the column_names list containing the names of all columns in the specified table.

def get_column_names(conn, table_name):
    """Return a list of column names."""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names

# This function provides a way to retrieve information about the tables and their columns in an SQLite database using a given connection object.
# The get_database_info function takes a connection object conn as input and returns a list of dictionaries. Each dictionary in the list represents a table in the database and contains the table name and its corresponding column names.
# Defines a function named get_database_info that takes a single parameter conn, which represents the connection object to the SQLite database.
# Initializes an empty list table_dicts to store the table names and column names.
# Iterate over each table name in the database by calling the get_table_names function, passing the conn object as an argument.
# Inside the loop, it calls the get_column_names function, passing the conn object and the current table_name as arguments. This retrieves the column names for the current table.
# It appends a new dictionary to the table_dicts list. The dictionary has two key-value pairs:
# "table_name": The key representing the table name, with the value being the current
# "column_names": The key representing the column names, with the value being the list of column names retrieved from the get_column_names function.
# After iterating over all tables, the function returns the table_dicts list containing the dictionaries representing each table in the database, along with their respective column names.

def get_database_info(conn):
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts


database_schema_dict = get_database_info(conn)
database_schema_string = "\n".join(
    [
        f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
        for table in database_schema_dict
    ]
)

# tool that represents a function called "ask_database". This function is designed to handle user questions about music by accepting a fully formed SQL query as input.
# The code you provided defines a list called tools that contains a single dictionary. This dictionary represents a tool, specifically a function, with the following properties:
# "type": Specifies the type of the tool, which is set to "function".
# "function": Contains information about the function itself, including its name, description, and parameters.
# "name": The name of the function, which is set to "ask_database".
# "description": A description of the function, which is set to "Use this function to answer user questions about music. Input should be a fully formed SQL query.".
# "parameters": A dictionary containing information about the parameters of the function.

tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {database_schema_string}
                                The query should be returned in plain text, not in JSON.
                                """,
                    }
                },
                "required": ["query"],
            },
        }
    }
]
# This function provides a way to execute SQL queries on an SQLite database using a given connection object and handle any exceptions that may occur during the execution.
# The ask_database function takes two parameters, conn and query, and is designed to query an SQLite database using a provided SQL query.
# It defines a function named ask_database that takes two parameters: conn, which represents the connection object to the SQLite database, and query, which is the SQL query to be executed.
# The function attempts to execute the SQL query using the execute method of the conn object. It then calls the fetchall method to retrieve all the rows returned by the query.
# The result of the fetchall method is converted to a string using the str function and assigned to the results variable.
# If the execution of the query encounters an exception, such as a syntax error or a database error, the code enters the except block.
# Inside the except block, the results variable is assigned a string that indicates the query failed, along with the specific error message. The error message is obtained from the exception object (e) using string formatting.
# Finally, the function returns the results variable, which contains either the string representation of the query results or the error message if the query failed.

def ask_database(conn, query):
    """Function to query SQLite database with a provided SQL query."""
    try:
        results = str(conn.execute(query).fetchall())
    except Exception as e:
        results = f"query failed with error: {e}"
    return results


# This function is designed to handle a specific type of message that includes function calls. If the function call is for "ask_database", it extracts the query and executes the ask_database function. 
# Otherwise, it returns an error message indicating that the function does not exist.
# It defines a function named execute_function_call that takes a single parameter message.
# The code checks if the value of the "name" property of the first function call in the message matches the string "ask_database". This is done by accessing the nested properties of the message dictionary using square brackets.
# If the condition is true, it extracts the value of the "query" property from the "arguments" property of the first function call using json.loads. This assumes that the "arguments" property is a JSON string that can be parsed into a dictionary.
# It then calls the ask_database function, passing the conn object and the extracted query as arguments, and assigns the result to the results variable.
# If the condition is false, meaning that the function name is not "ask_database", it assigns an error message to the results variable. The error message includes the name of the non-existing function obtained from the message.
# Finally, the function returns the results variable, which contains either the results of the ask_database function or an error message if the function name is not "ask_database".

def execute_function_call(message):
    if message["tool_calls"][0]["function"]["name"] == "ask_database":
        print(message)
        query = json.loads(message["tool_calls"][0]["function"]["arguments"])["query"]
        results = ask_database(conn, query)
    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results



