from fasthtml.common import *
from claudette import *
from prompts import *

import os
import re
import json
import anthropic
from config import ANTHROPIC_API_KEY

# Set the environment variable from the config
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY

# Raw HTML class to render unescaped HTML
class Raw:
    def __init__(self, html):
        self.html = html
    def __str__(self):
        return self.html

# Set up the app with Apple-inspired design using Tailwind
apple_theme = """
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'apple-blue': '#007AFF',
        'apple-gray': '#8E8E93',
        'apple-light-gray': '#F2F2F7',
        'apple-green': '#34C759',
        'user-bubble': 'rgba(0, 122, 255, 0.1)',
        'assistant-bubble': 'rgba(229, 229, 234, 0.8)'
      },
      fontFamily: {
        'sf': ['-apple-system', 'BlinkMacSystemFont', 'San Francisco', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif']
      },
      boxShadow: {
        'apple': '0 1px 2px rgba(0, 0, 0, 0.05)'
      }
    }
  }
}
</script>
<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #FFFFFF;
  color: #1D1D1F;
}
.chat-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.4;
  word-wrap: break-word;
  position: relative;
}
.typing-indicator span {
  animation: typing 1.5s infinite;
}
.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes typing {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
"""

hdrs = (picolink, Script(src="https://cdn.tailwindcss.com"), Raw(apple_theme))
app = FastHTML(hdrs=hdrs, cls="max-w-2xl mx-auto p-4 font-sf bg-white sm:py-6")

# Set up Anthropic client with the Claude 3 Sonnet model
client = anthropic.Anthropic()
model = "claude-3-5-sonnet-20240620"

# Function implementations
def calculate_savings_plan(goal_amount, time_frame_months, current_savings=0):
    """Calculate the required monthly savings to reach a financial goal and return FastHTML visualization"""
    remaining_amount = goal_amount - current_savings
    monthly_savings = remaining_amount / time_frame_months
    
    # Create data for visualization
    months = list(range(0, time_frame_months + 1))
    savings_progression = [current_savings + (monthly_savings * i) for i in months]
    
    # Scale values for the graph
    max_value = goal_amount * 1.1  # Add some padding
    graph_height = 200
    scaled_values = [int((val / max_value) * graph_height) for val in savings_progression]
    
    # Generate the FastHTML graph
    graph_html = generate_savings_graph(months, savings_progression, scaled_values, graph_height, goal_amount, monthly_savings, time_frame_months, current_savings)
    
    # Return both calculation and visualization
    return {
        "monthly_savings": round(monthly_savings, 2),
        "total_amount": goal_amount,
        "time_frame_months": time_frame_months,
        "current_savings": current_savings,
        "visualization": graph_html
    }

def generate_savings_graph(months, savings_progression, scaled_values, graph_height, goal_amount, monthly_savings, time_frame_months, current_savings):
    """Generate FastHTML code for a savings growth visualization"""
    # Create a responsive container for the chart
    container = Div(cls="w-full bg-white rounded-lg shadow-sm p-4 mb-4")
    
    # Chart title and summary
    container(
        Div(cls="text-lg font-semibold mb-2")("Savings Growth Projection"),
        Div(cls="text-sm text-gray-600 mb-4")(
            f"Monthly savings: ${round(monthly_savings, 2)} for {time_frame_months} months to reach ${round(goal_amount, 2)}"
        )
    )
    
    # Graph container
    graph = Div(cls="relative h-64 mt-4")
    
    # Y-axis labels and grid lines
    y_labels = Div(cls="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-500")
    y_labels(
        Div(cls="text-right pr-2")(f"${round(goal_amount, 2)}"),
        Div(cls="text-right pr-2")(f"${round(goal_amount * 0.75, 2)}"),
        Div(cls="text-right pr-2")(f"${round(goal_amount * 0.5, 2)}"),
        Div(cls="text-right pr-2")(f"${round(goal_amount * 0.25, 2)}"),
        Div(cls="text-right pr-2")("$0")
    )
    
    # Create the chart area
    chart_area = Div(cls="absolute left-14 right-0 top-0 bottom-0")
    
    # Horizontal grid lines
    grid_lines = Div(cls="absolute inset-0 flex flex-col justify-between")
    for i in range(5):
        grid_lines(Div(cls="border-t border-gray-200 w-full h-0"))
    
    # Goal line
    goal_line = Div(cls="absolute top-0 left-0 right-0 border-t-2 border-dashed border-red-400 flex justify-end")
    goal_line(Div(cls="bg-red-400 text-white text-xs px-1 rounded-sm")("Goal"))
    
    # Chart data visualization - we'll use SVG for the line graph
    chart_svg = Raw(f"""
    <svg class="w-full h-full overflow-visible">
        <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="rgba(0, 122, 255, 0.5)"/>
                <stop offset="100%" stop-color="rgba(0, 122, 255, 0.1)"/>
            </linearGradient>
        </defs>
        
        <!-- Area under the curve -->
        <path d="M{0},{graph_height} {" ".join([f"L{i * (100 / time_frame_months)}%,{graph_height - scaled_values[i]}" for i in range(len(months))])} L{100}%,{graph_height} Z" 
              fill="url(#gradient)" stroke="none" />
              
        <!-- Line graph -->
        <path d="M{0},{graph_height - scaled_values[0]} {" ".join([f"L{i * (100 / time_frame_months)}%,{graph_height - scaled_values[i]}" for i in range(1, len(months))])}" 
              fill="none" stroke="#007AFF" stroke-width="2" />
              
        <!-- Data points -->
        {"".join([f'<circle cx="{i * (100 / time_frame_months)}%" cy="{graph_height - scaled_values[i]}" r="3" fill="#007AFF" />' for i in range(0, len(months), max(1, time_frame_months // 6))])}
    </svg>
    """)
    
    # X-axis labels
    x_labels = Div(cls="flex justify-between text-xs text-gray-500 mt-2")
    label_count = min(6, time_frame_months)
    step = time_frame_months / label_count
    for i in range(label_count + 1):
        month = int(i * step)
        x_labels(Div()(f"Month {month}"))
    
    # Add everything to the chart area
    chart_area(grid_lines, chart_svg)
    
    # Combine all elements
    graph(y_labels, chart_area)
    
    # Add X-axis labels below the graph
    container(graph, x_labels)
    
    # Key metrics cards
    metrics = Div(cls="grid grid-cols-2 gap-4 mt-4")
    metrics(
        Div(cls="bg-apple-light-gray rounded-lg p-3")(
            Div(cls="text-xs text-gray-500")("Monthly Savings"),
            Div(cls="text-lg font-semibold")(f"${round(monthly_savings, 2)}")
        ),
        Div(cls="bg-apple-light-gray rounded-lg p-3")(
            Div(cls="text-xs text-gray-500")("Total Goal"),
            Div(cls="text-lg font-semibold")(f"${round(goal_amount, 2)}")
        ),
        Div(cls="bg-apple-light-gray rounded-lg p-3")(
            Div(cls="text-xs text-gray-500")("Time Frame"),
            Div(cls="text-lg font-semibold")(f"{time_frame_months} months")
        ),
        Div(cls="bg-apple-light-gray rounded-lg p-3")(
            Div(cls="text-xs text-gray-500")("Current Savings"),
            Div(cls="text-lg font-semibold")(f"${round(current_savings, 2)}")
        )
    )
    
    container(metrics)
    
    return container

def estimate_cost(goal_type, goal_details):
    """Estimate the cost of a financial goal based on the type and details"""
    # This would typically involve more complex logic or external API calls
    estimates = {
        "travel": {
            "budget": 1200,
            "standard": 2500,
            "luxury": 5000
        },
        "purchase": {
            "electronics": 800,
            "appliances": 1200,
            "vehicle": 15000
        },
        "education": {
            "course": 800,
            "certificate": 2000,
            "degree": 50000
        }
    }
    
    # Simple estimation based on predefined values
    if goal_type.lower() in estimates:
        category = estimates[goal_type.lower()]
        # Return medium range as default estimate
        return {
            "estimated_cost": list(category.values())[1],
            "range": category,
            "goal_type": goal_type,
            "details": goal_details
        }
    
    # Default fallback
    return {
        "estimated_cost": 1000,
        "goal_type": goal_type,
        "details": goal_details,
        "note": "Generic estimate provided; please provide more specific details"
    }

# Function registry
available_functions = {
    "calculate_savings_plan": calculate_savings_plan,
    "estimate_cost": estimate_cost
}

def ChatMessage(msg, user):
    if user:
        bubble_class = "bg-user-bubble text-gray-800"
        chat_class = "flex justify-end"
        avatar = Div(cls="h-8 w-8 rounded-full bg-apple-blue flex items-center justify-center text-white text-xs font-medium mr-2 mb-auto mt-1")("You")
    else:
        bubble_class = "bg-assistant-bubble text-gray-800"
        chat_class = "flex justify-start"
        avatar = Div(cls="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center text-white text-xs font-medium ml-2 mb-auto mt-1")("AI")
    
    bubble = Div(msg, cls=f"chat-bubble {bubble_class}")
    
    if user:
        return Div(cls=f"{chat_class} mb-4")(
            bubble,
            avatar
        )
    else:
        return Div(cls=f"{chat_class} mb-4")(
            avatar,
            bubble
        )

# The input field for the user message
def ChatInput():
    return Div(cls="relative")(
        Input(name='msg', id='msg-input', placeholder="Type a message...",
             cls="w-full py-3.5 px-4 pr-12 rounded-2xl border border-gray-200 focus:border-apple-blue focus:ring-1 focus:ring-apple-blue outline-none transition-all duration-200 shadow-sm", 
             hx_swap_oob='true'),
        Button(cls="absolute right-3 top-1/2 transform -translate-y-1/2 bg-apple-blue hover:bg-blue-600 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors duration-200 focus:outline-none")(
            Raw('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" /></svg>')
        )
    )

# The main screen
@app.get
def index():
    page = Div(cls="flex flex-col h-screen")(
        # Header
        Div(cls="py-4 border-b border-gray-100 mb-2")(
            Div(cls="text-center")(
                Div("Financial Goal Planner", cls="text-xl font-semibold text-gray-800"),
                Div("Chat with an AI financial assistant", cls="text-sm text-gray-500 mt-1")
            )
        ),
        # Chat container
        Form(hx_post=send, hx_target="#chatlist", hx_swap="beforeend", cls="flex-1 flex flex-col h-full")(
            # Messages area
            Div(id="chatlist", cls="flex-1 overflow-y-auto px-2 py-4 space-y-2"),
            # Input area
            Div(cls="pt-3 border-t border-gray-100 mt-auto")(
                ChatInput()
            )
        )
    )
    return Titled('Financial Goal Planner', page)

def parse_options(response):
    """Parse options from model response if they exist"""
    # Look for lists of options in different formats
    options = []
    
    # Format: Options: Option1 | Option2 | Option3 | Option4
    option_line = re.search(r'Options:\s*(.*?)(?:\n|$)', response)
    if option_line:
        options = [opt.strip() for opt in option_line.group(1).split('|')]
    
    # Format with numbered list: 1. Option1, 2. Option2, etc.
    elif re.search(r'\d+\.\s+\w+', response):
        numbered_options = re.findall(r'\d+\.\s+(.*?)(?=\n\d+\.|\n\n|$)', response)
        if numbered_options and len(numbered_options) <= 4:
            options = [opt.strip() for opt in numbered_options]
    
    return options, response

def OptionButtons(options):
    """Generate a set of buttons for the options"""
    if not options:
        return Div()
    
    buttons_list = []
    for option in options:
        buttons_list.append(
            Button(option, 
                  cls="w-full px-4 py-2.5 mb-2 bg-apple-light-gray border-none rounded-xl text-sm font-medium text-gray-800 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-apple-blue focus:ring-opacity-50 transition-all duration-200 shadow-apple", 
                  hx_post="/select_option",
                  hx_vals=f'{{"option": "{option}"}}',
                  hx_target="#chatlist",
                  hx_swap="beforeend")
        )
    return Div(cls="flex flex-col gap-1 my-4 px-2 w-full")(*buttons_list)

def handle_function_calls(message_content):
    """Parse and execute function calls from the message content"""
    if not hasattr(message_content, "tool_calls") or not message_content.tool_calls:
        return None
    
    function_results = []
    for tool_call in message_content.tool_calls:
        function_name = tool_call.name
        function_args = json.loads(tool_call.input)
        
        if function_name in available_functions:
            function_to_call = available_functions[function_name]
            function_response = function_to_call(**function_args)
            function_results.append({
                "function_name": function_name,
                "args": function_args,
                "result": function_response
            })
    
    return function_results

@app.post
def send(msg:str, messages:list[str]=None):
    if not messages: messages = []
    
    # Add the user message to the history
    messages.append(msg.rstrip())
    
    # Build the messages for the Anthropic API
    api_messages = []
    for i, message in enumerate(messages):
        role = "user" if i % 2 == 0 else "assistant"
        api_messages.append({"role": role, "content": message})
    
    # If the last message is from the assistant, remove it (shouldn't happen)
    if len(api_messages) > 0 and api_messages[-1]["role"] == "assistant":
        api_messages.pop()
    
    # Build the system prompt from our template
    system_prompt = INPUT_GATHERING_PROMPT
    
    # Call the Anthropic API with function calling enabled
    print(api_messages)
    print(model)
    response = client.messages.create(
        model=model,
        max_tokens=150,
        system=system_prompt,
        messages=api_messages,
        top_p=0.95,
        temperature=0.01,
        tools=[
            {
                "name": "calculate_savings_plan",
                "description": "Calculate the required monthly savings to reach a financial goal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal_amount": {
                            "type": "number",
                            "description": "The total amount of money needed to reach the goal"
                        },
                        "time_frame_months": {
                            "type": "number",
                            "description": "The number of months available to save for the goal"
                        }
                    },
                    "required": ["goal_amount", "time_frame_months"]
                }
            },
            {
                "name": "estimate_cost",
                "description": "Estimate the cost of a financial goal based on the type and details",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal_type": {
                            "type": "string",
                            "description": "The type of financial goal (e.g., travel, purchase, education)"
                        },
                        "goal_details": {
                            "type": "string",
                            "description": "Specific details about the goal"
                        }
                    },
                    "required": ["goal_type", "goal_details"]
                }
            }
        ]
    )
    
    # Handle any function calls
    function_results = handle_function_calls(response.content[0])
    
    # Get the text response
    r = response.content[0].text
    
    # If there were function results, append them to the messages
    if function_results:
        function_response = json.dumps(function_results, indent=2)
        # Add the function results to the message history as a system message (invisible to user)
        messages.append(f"FUNCTION_RESULTS: {function_response}")
        
        # If there were function calls, we need to send another request to get the final response
        api_messages.append({"role": "assistant", "content": [
            {"type": "tool_calls", "tool_calls": response.content[0].tool_calls},
        ]})
        api_messages.append({"role": "tool", "content": function_response, "tool_call_id": response.content[0].tool_calls[0].id})
        
        # Get final response after function call
        final_response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system_prompt,
            messages=api_messages
        )
        r = final_response.content[0].text
    
    # Parse options if present in the response and remove them from displayed text
    options, r = parse_options(r)
    
    # Remove options text pattern "Options: Option1 | Option2 | Option3 | Option4" from the response
    r = re.sub(r'Options:\s*.*?(?=\n|$)', '', r).strip()
    
    # Remove numbered list format options
    if options:
        for i, option in enumerate(options, 1):
            r = re.sub(rf'{i}\.\s+{re.escape(option)}.*?(?=\n\d+\.|\n\n|$)', '', r)
    
    # Clean up any extra newlines
    r = re.sub(r'\n{3,}', '\n\n', r).strip()
    
    # Add the assistant response to the history
    messages.append(r)
    
    # Create hidden fields for all messages
    hidden_messages = [Hidden(m, name="messages") for m in messages]
    
    response_elements = [
        ChatMessage(msg, True),    # The user's message
        ChatMessage(r, False), # The chatbot's response
        *hidden_messages,  # Include all messages as hidden fields
        ChatInput() # And clear the input field via an OOB swap
    ]
    
    # Add visualization if calculate_savings_plan was called
    if function_results:
        for func_result in function_results:
            if func_result["function_name"] == "calculate_savings_plan" and "visualization" in func_result["result"]:
                response_elements.append(Div(cls="mt-4")(func_result["result"]["visualization"]))
    
    # Add option buttons if found
    if options:
        response_elements.append(OptionButtons(options))
    
    return tuple(response_elements)

@app.post("/select_option")
def select_option(option:str, messages:list[str]=None):
    """Handle when user selects an option button"""
    if not messages: messages = []
    
    # Format the selection with context
    selection_message = f"Selected: {option}"
    messages.append(selection_message)
    
    # Build the messages for the Anthropic API
    api_messages = []
    for i, message in enumerate(messages):
        # Skip any function results messages
        if message.startswith("FUNCTION_RESULTS:"):
            continue
            
        role = "user" if i % 2 == 0 else "assistant"
        api_messages.append({"role": role, "content": message})
    
    # If the last message is from the assistant, remove it (shouldn't happen)
    if len(api_messages) > 0 and api_messages[-1]["role"] == "assistant":
        api_messages.pop()
    
    # Build the system prompt from our template
    system_prompt = INPUT_GATHERING_PROMPT
    
    # Call the Anthropic API with function calling enabled
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system=system_prompt,
        messages=api_messages,
        tools=[
            {
                "name": "calculate_savings_plan",
                "description": "Calculate the required monthly savings to reach a financial goal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal_amount": {
                            "type": "number",
                            "description": "The total amount of money needed to reach the goal"
                        },
                        "time_frame_months": {
                            "type": "number",
                            "description": "The number of months available to save for the goal"
                        }
                    },
                    "required": ["goal_amount", "time_frame_months"]
                }
            },
        ]
    )
    
    # Handle any function calls
    function_results = handle_function_calls(response.content[0])
    
    # Get the text response
    r = response.content[0].text
    
    # If there were function results, append them to the messages
    if function_results:
        function_response = json.dumps(function_results, indent=2)
        # Add the function results to the message history as a system message (invisible to user)
        messages.append(f"FUNCTION_RESULTS: {function_response}")
        
        # If there were function calls, we need to send another request to get the final response
        api_messages.append({"role": "assistant", "content": [
            {"type": "tool_calls", "tool_calls": response.content[0].tool_calls},
        ]})
        api_messages.append({"role": "tool", "content": function_response, "tool_call_id": response.content[0].tool_calls[0].id})
        
        # Get final response after function call
        final_response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system_prompt,
            messages=api_messages
        )
        r = final_response.content[0].text
    
    # Parse options if present in the response and remove them from displayed text
    options, r = parse_options(r)
    
    # Remove options text pattern "Options: Option1 | Option2 | Option3 | Option4" from the response
    r = re.sub(r'Options:\s*.*?(?=\n|$)', '', r).strip()
    
    # Remove numbered list format options
    if options:
        for i, option in enumerate(options, 1):
            r = re.sub(rf'{i}\.\s+{re.escape(option)}.*?(?=\n\d+\.|\n\n|$)', '', r)
    
    # Clean up any extra newlines
    r = re.sub(r'\n{3,}', '\n\n', r).strip()
    
    # Add the assistant response to the history
    messages.append(r)
    
    # Create hidden fields for all messages
    hidden_messages = [Hidden(m, name="messages") for m in messages]
    
    response_elements = [
        ChatMessage(selection_message, True),
        ChatMessage(r, False),
        *hidden_messages,  # Include all messages as hidden fields
        ChatInput()
    ]
    
    # Add visualization if calculate_savings_plan was called
    if function_results:
        for func_result in function_results:
            if func_result["function_name"] == "calculate_savings_plan" and "visualization" in func_result["result"]:
                response_elements.append(Div(cls="mt-4")(func_result["result"]["visualization"]))
    
    if options:
        response_elements.append(OptionButtons(options))
    
    return tuple(response_elements)

serve()