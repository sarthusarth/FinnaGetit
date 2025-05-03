from fasthtml.common import *
from claudette import *
from prompts import *
from theme import modern_theme
import os
import re
import json
import anthropic
from config import ANTHROPIC_API_KEY
from goal_storage import save_goal, load_goals, get_latest_goal, delete_goal
from datetime import datetime
from dashboard import generate_dashboard
from starlette.responses import HTMLResponse

# Set the environment variable from the config
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY

# Raw HTML class to render unescaped HTML
class Raw:
    def __init__(self, html):
        self.html = html
    def __str__(self):
        return self.html

hdrs = (picolink, Script(src="https://cdn.tailwindcss.com"), Raw(modern_theme))
app = FastHTML(hdrs=hdrs, cls="max-w-2xl mx-auto p-4 font-sans bg-white shadow-md sm:py-6")

# Global variable to store the latest savings plan visualization
latest_plan_visualization = None

# Set up Anthropic client with the Claude 3 Sonnet model
client = anthropic.Anthropic()
#model = "claude-3-7-sonnet-20250219"
model = "claude-3-5-sonnet-20240620"
# Function implementations
def calculate_savings_plan(goal_amount, time_frame_months, goal="Savings Plan Trip", current_savings=0):
    """Calculate the required monthly savings to reach a financial goal and return HTML visualization"""
    try:
        # Convert inputs to float/int if they're not already and ensure they're valid
        goal_amount = float(goal_amount)
        time_frame_months = int(time_frame_months)
        current_savings = float(current_savings)
        
        # Validate inputs to ensure they're reasonable
        if goal_amount <= 0:
            raise ValueError("Goal amount must be greater than zero")
        if time_frame_months <= 0:
            raise ValueError("Time frame must be greater than zero")
        if current_savings < 0:
            raise ValueError("Current savings cannot be negative")
        if current_savings >= goal_amount:
            # Goal already achieved
            monthly_savings = 0
        else:
            remaining_amount = goal_amount - current_savings
            monthly_savings = remaining_amount / time_frame_months
        
        # Create data for the graph
        months = list(range(0, time_frame_months + 1))
        savings_progression = [current_savings + (monthly_savings * i) for i in months]
        
        
        # Generate dashboard HTML with rounded values to avoid precision issues
        dashboard_html = generate_dashboard(
                goal="Saving Plan",
                duration=time_frame_months,
                amount=goal_amount,
            )
        with open("./dashboard_filled.html", "w") as file:
            file.write(dashboard_html)


            # Continue even if dashboard generation fails
        
        # Create a simplified HTML visualization
        html = f"""
        
        <div class="savings-plan bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <div class="text-lg font-semibold text-gray-900">{goal}</div>
                <div class="text-sm font-medium text-blue-600">€{goal_amount:,.2f}</div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-600">Time Frame</div>
                    <div class="text-lg font-medium text-gray-900">{time_frame_months} months</div>
                </div>
                <div class="p-3 bg-gray-50 rounded-lg">
                    <div class="text-sm text-gray-600">Current Savings</div>
                    <div class="text-lg font-medium text-gray-900">€{current_savings:,.2f}</div>
                </div>
            </div>
            
            <div class="mb-4">
                <div class="flex justify-between mb-1">
                    <div class="text-sm font-medium text-gray-600">Monthly Savings Target</div>
                    <div class="text-sm font-medium text-blue-600">€{monthly_savings:,.2f}</div>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-blue-600 h-2.5 rounded-full" style="width: {min(100, round((current_savings / goal_amount) * 100))}%"></div>
                </div>
                <div class="text-xs text-gray-500 mt-1">{min(100, round((current_savings / goal_amount) * 100))}% of goal</div>
            </div>
            
            <div class="border-t border-gray-200 pt-4">
                <div class="text-sm font-medium text-gray-900 mb-2">Savings Projection</div>
                <div class="flex items-center">
                    <div class="flex-1 flex items-center">
                        <div class="w-3 h-3 rounded-full bg-blue-600 mr-2"></div>
                        <div class="text-xs text-gray-600">Now: €{current_savings:,.2f}</div>
                    </div>
                    <div class="flex-1 text-center">
                        <div class="text-xs text-gray-600">→</div>
                    </div>
                    <div class="flex-1 flex items-center justify-end">
                        <div class="text-xs text-gray-600">Goal: €{goal_amount:,.2f}</div>
                        <div class="w-3 h-3 rounded-full bg-green-600 ml-2"></div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Save the goal to persistent storage - for demo, we'll overwrite the existing goal
        goal_data = {
            "id": 1,  # Always use ID 1 for the single goal
            "goal_amount": round(goal_amount, 2),
            "time_frame_months": time_frame_months,
            "current_savings": round(current_savings, 2),
            "monthly_savings": round(monthly_savings, 2),
            "created_at": datetime.now().isoformat()
        }
        # For demo, directly overwrite the goal instead of adding to a list
        save_goal(goal_data, overwrite=True)
        
        return html
    except Exception as e:
        print(f"Error in calculate_savings_plan: {str(e)}")
        # Return a simple error message as HTML
        return f"""
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <strong>Error:</strong> Unable to generate savings plan. Please try again.
        </div>
        """

# Function registry
available_functions = {
    "calculate_savings_plan": calculate_savings_plan,
}

def ChatMessage(msg, user):
    if user:
        bubble_class = "bg-blue-100 text-blue-900 border border-blue-200"
        chat_class = "flex justify-end"
        avatar = Div(cls="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-medium mr-2 mb-auto mt-1")("You")
    else:
        bubble_class = "bg-white text-gray-900 border border-gray-200"
        chat_class = "flex justify-start"
        avatar = Div(cls="h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center text-white text-xs font-medium ml-2 mb-auto mt-1")("AI")
    
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
             cls="w-full py-3 px-4 pr-12 rounded-lg border border-gray-300 bg-white text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all duration-200"),
        Button(cls="absolute right-3 top-1/2 transform -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors duration-200 focus:outline-none")(
            Raw('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" /></svg>')
        )
    )

# Function to handle tab switching logic with improved styling
def handle_tab_switch(active_tab="goal_setting"):
    return Div(cls="flex border-b border-gray-200 mb-4 px-4 pt-2 bg-white")(
        Button("Goal Setting", 
               cls=f"py-3 px-6 text-center font-medium text-sm {'bg-blue-600 text-white' if active_tab == 'goal_setting' else 'bg-gray-100 text-gray-700'} rounded-t-lg mr-2",
               hx_get="/tab/goal_setting",
               hx_target="#app-content",
               hx_swap="outerHTML",
               hx_push_url="false"),
        Button("My Goals", 
               cls=f"py-3 px-6 text-center font-medium text-sm {'bg-blue-600 text-white' if active_tab == 'goal_plan' else 'bg-gray-100 text-gray-700'} rounded-t-lg",
               hx_get="/tab/goal_plan",
               hx_target="#app-content",
               hx_swap="outerHTML",
               hx_push_url="false")
    )

# Tab content for Goal Setting
@app.get("/tab/goal_setting")
def tab_goal_setting():
    return Div(id="app-content", cls="flex-1 flex flex-col overflow-auto")(
        Form(hx_post=send, hx_target="#chatlist", hx_swap="beforeend", cls="flex-1 flex flex-col h-full")(
            # Messages area
            Div(id="chatlist", cls="flex-1 overflow-y-auto px-2 py-4 space-y-2"),
            # Input area
            Div(cls="pt-3 border-t border-neutral-light mt-auto")(
                ChatInput()
            )
        )
    )

# Tab content for Goal Plan
@app.get("/tab/goal_plan")
def tab_goal_plan():
    # Get the single saved goal
    all_goals = load_goals()
    
    # Default content if no goal has been created yet
    if not all_goals:
        return Div(id="app-content", cls="flex-1 flex flex-col overflow-auto")(
            Div(cls="flex flex-col items-center justify-center p-10 text-center h-64 bg-white rounded-lg shadow border border-gray-200 m-4")(
                Raw('<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-12 h-12 text-gray-500 mb-4"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l .415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>'),
                Div(cls="text-xl font-semibold text-gray-800 mb-3")("No Goal Created Yet"),
                Div(cls="text-gray-600 max-w-md")("Chat with the AI assistant in the Goal Setting tab to create your financial plan. Set a savings goal and timeframe to visualize your path to success."),
                Button("Go to Goal Setting", 
                    cls="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors",
                    hx_get="/tab/goal_setting",
                    hx_target="#app-content",
                    hx_swap="outerHTML",
                    hx_push_url="false")
            )
        )
    else:
        # Get the single goal to display
        goal = all_goals[0]
        
        # Extract data for visualization
        goal_amount = goal["goal_amount"]
        time_frame_months = goal["time_frame_months"]
        current_savings = goal.get("current_savings", 0)
        
        # Generate the dashboard HTML directly
        goal_visualization = calculate_savings_plan(
            goal_amount=goal_amount,
            time_frame_months=time_frame_months,
            current_savings=current_savings
        )
        
        # Simplified UI for demo mode with a single goal
        return Div(id="app-content", cls="flex-1 flex flex-col overflow-auto")(
            # Header with buttons
            Div(cls="flex justify-end p-4 sticky top-0 bg-white z-10 border-b border-gray-100")(
                Div(cls="flex items-center gap-2")(
                    Button("Create New Goal", 
                        cls="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm",
                        hx_get="/tab/goal_setting",
                        hx_target="#app-content",
                        hx_swap="outerHTML",
                        hx_push_url="false"),
                    Button(
                        cls="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors text-sm flex items-center",
                        hx_post="/delete_goal",
                        hx_vals='{"goal_id": 1}',
                        hx_target="#app-content",
                        hx_swap="outerHTML",
                        hx_confirm="Are you sure you want to delete your goal?"
                    )(
                        Raw('<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>'),
                        "Delete"
                    )
                )
            ),
            
            # Goal visualization
            Div(cls="p-4 mb-6")(
                Div(cls="flex justify-between items-center mb-4")(
                    Div(cls="text-lg font-semibold text-neutral-dark")("Your Savings Plan"),
                    Div(cls="text-xs text-gray-500")("Created on " + datetime.fromisoformat(goal.get("created_at", datetime.now().isoformat())).strftime("%b %d, %Y"))
                ),
                Raw(goal_visualization),
                
                # Goal details in a nice format
                Div(cls="bg-white rounded-lg p-4 mt-4 border border-gray-200 shadow-sm")(
                    Div(cls="text-xl font-bold mb-4 text-gray-800 border-b pb-2")("Goal Details"),
                    Div(cls="mb-4")(
                        Table(cls="w-full")(
                            Tr(
                                Td(cls="py-2 pl-0 pr-4 text-sm text-gray-600 font-medium w-1/3")("Goal Amount:"),
                                Td(cls="py-2 px-2 text-sm font-medium text-gray-900")(f"€{goal['goal_amount']:,.2f}")
                            ),
                            Tr(
                                Td(cls="py-2 pl-0 pr-4 text-sm text-gray-600 font-medium")("Time Frame:"),
                                Td(cls="py-2 px-2 text-sm font-medium text-gray-900")(f"{goal['time_frame_months']} months")
                            ),
                            Tr(
                                Td(cls="py-2 pl-0 pr-4 text-sm text-gray-600 font-medium")("Monthly Savings:"),
                                Td(cls="py-2 px-2 text-sm font-medium text-gray-900")(f"€{goal['monthly_savings']:,.2f}")
                            ),
                            Tr(
                                Td(cls="py-2 pl-0 pr-4 text-sm text-gray-600 font-medium")("Current Savings:"),
                                Td(cls="py-2 px-2 text-sm font-medium text-gray-900")(f"€{goal.get('current_savings', 0):,.2f}")
                            ),
                            Tr(
                                Td(cls="py-2 pl-0 pr-4 text-sm text-gray-600 font-medium")("Progress:"),
                                Td(cls="py-2 px-2 text-sm font-medium text-gray-900")(f"{min(100, round((current_savings / goal_amount) * 100))}%")
                            )
                        )
                    ),
                    # Add View more details button
                    Button("View Dashboard", 
                        cls="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors",
                        onclick="window.location.href='/dashboard'")
                )
            )
        )

# Add new endpoint to handle goal deletion
@app.post("/delete_goal")
def handle_delete_goal(goal_id:int):
    """Handle deletion of a goal"""
    # Call the delete_goal function from goal_storage
    delete_goal(goal_id)
    
    # Redirect back to the goal plan tab
    return tab_goal_plan()

# For demo mode, we don't need the view_goal endpoint since we only have one goal

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
                  cls="w-full px-4 py-3 mb-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-200", 
                  hx_post="/select_option",
                  hx_vals=f'{{"option": "{option}"}}',
                  hx_target="#chatlist",
                  hx_swap="beforeend")
        )
    return Div(cls="flex flex-col gap-2 my-4 px-2 w-full")(*buttons_list)

def handle_function_calls(message_content):
    """Parse and execute function calls from the message content"""
    print("Checking for tool calls in message content")
    # Check if this is a ToolUseBlock
    if message_content.__class__.__name__ == "ToolUseBlock":
        print(f"Processing tool call: {message_content.name}")
        try:
            function_name = message_content.name
            # Check if input is already a dict or needs to be parsed
            if isinstance(message_content.input, dict):
                function_args = message_content.input
            else:
                function_args = json.loads(message_content.input)
            print(f"Function args: {function_args}")
            
            if function_name in available_functions:
                function_to_call = available_functions[function_name]
                print(f"Executing function {function_name} with args {function_args}")
                function_response = function_to_call(**function_args)
                print(f"Function executed successfully")
                return [{"function_name": function_name, "result": function_response}]
            else:
                print(f"Function {function_name} not found in available_functions")
                return None
        except Exception as e:
            print(f"Error processing function call: {str(e)}")
            return None
    
    print("No tool calls found in this content block")
    return None

@app.post
def send(msg:str, messages:list[str]=None):
    global latest_plan_visualization
    
    if not messages: messages = []
    
    # Add the user message to the history
    messages.append(msg.rstrip())
    
    # Build the messages for the Anthropic API
    api_messages = []
    for i, message in enumerate(messages):
        # Skip any empty messages or function results
        if not message.strip() or message.startswith("FUNCTION_RESULTS:"):
            continue
            
        role = "user" if i % 2 == 0 else "assistant"
        api_messages.append({"role": role, "content": message})
    
    # If the last message is from the assistant, remove it (shouldn't happen)
    if len(api_messages) > 0 and api_messages[-1]["role"] == "assistant":
        api_messages.pop()
    
    # Make sure we have valid messages - should be at least one user message
    if not api_messages or not any(msg["role"] == "user" for msg in api_messages):
        # Create a default message if necessary
        api_messages = [{"role": "user", "content": "Hello"}]
    
    # Build the system prompt from our template
    system_prompt = INPUT_GATHERING_PROMPT
    
    # Call the Anthropic API with function calling enabled
    response = client.messages.create(
        model=model,
        max_tokens=350,
        system=system_prompt,
        messages=api_messages,
        top_p=0.95,
        temperature=0.01,
        tools=[
            {
                "name": "calculate_savings_plan",
                "description": "Calculates the plan to save money to reach the goal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the user"
                        },
                        "goal_amount": {
                            "type": "number",
                            "description": "The total amount of money needed to reach the goal"
                        },
                        "time_frame_months": {
                            "type": "number",
                            "description": "The number of months available to save for the goal"
                        },
                    },
                    "required": ["goal", "goal_amount", "time_frame_months"]
                }
            }
        ],
        tool_choice={"type": "auto"},
    )
    print(messages)
    print(response)

    # Debug print statements
    print("Response content:", response.content)
    print("Response content type:", type(response.content))
    print("Content length:", len(response.content))

    # Properly check each content block
    for i, block in enumerate(response.content):
        print(f"\nBlock {i} type:", type(block))
        print(f"Block {i} class name:", block.__class__.__name__)
        
        # Check if this is a ToolUseBlock
        if block.__class__.__name__ == "ToolUseBlock":
            print(f"TOOL CALL FOUND in block {i}:")
            print(f"  Tool name: {block.name}")
            print(f"  Tool input: {block.input}")
    
    # Check for and handle any function calls in the response
    function_results = None
    
    for block in response.content:
        if block.__class__.__name__ == "ToolUseBlock":
            function_results = handle_function_calls(block)
            break
    
    # If there are function results, immediately redirect to graph without further API calls
    if function_results:
        # Store the HTML visualization for later use
        if function_results[0]["function_name"] == "calculate_savings_plan":
            latest_plan_visualization = function_results[0]["result"]
        
        # Add hidden messages to the form
        hidden_messages = [Hidden(m, name="messages") for m in messages]
        
        # Add a success message to the chat history
        success_message = "Your savings plan has been created successfully!"
        messages.append(success_message)
        
        # Create a response that will be displayed in the chat history first
        # before redirecting to the Goal Plan tab
        return (
            ChatMessage(msg, True),
            ChatMessage(success_message, False),
            *hidden_messages,
            ChatInput(),
            Raw("""
            <script>
                // Reset any existing form state first
                document.querySelector('#msg-input').value = '';
                
                // Wait a short moment before switching tabs to ensure the message is displayed
                setTimeout(function() {
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', '/tab/goal_plan');
                    xhr.onload = function() {
                        if (xhr.status === 200) {
                            document.getElementById('app-content').outerHTML = xhr.responseText;
                            // Update tab appearance
                            document.querySelectorAll('button').forEach(function(btn) {
                                if (btn.textContent.trim() === 'Goal Plan') {
                                    btn.classList.add('bg-blue-600', 'text-white');
                                    btn.classList.remove('bg-gray-100', 'text-gray-700');
                                } else if (btn.textContent.trim() === 'Goal Setting') {
                                    btn.classList.add('bg-gray-100', 'text-gray-700');
                                    btn.classList.remove('bg-blue-600', 'text-white');
                                }
                            });
                        }
                    };
                    xhr.send();
                }, 500);
            </script>
            """)
        )
    
    # If no function calls, continue with normal text response processing
    # Get the text response (find the first TextBlock)
    r = ""
    for block in response.content:
        if block.__class__.__name__ == "TextBlock":
            r = block.text
            break
    
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
    
    # Add option buttons if found
    if options:
        response_elements.append(OptionButtons(options))
    
    return tuple(response_elements)

@app.post("/select_option")
def select_option(option:str, messages:list[str]=None):
    """Handle when user selects an option button"""
    global latest_plan_visualization
    
    if not messages: messages = []
    
    # Format the selection with context
    selection_message = f"Selected: {option}"
    messages.append(selection_message)
    
    # Build the messages for the Anthropic API
    api_messages = []
    for i, message in enumerate(messages):
        # Skip any function results messages or empty messages
        if message.startswith("FUNCTION_RESULTS:") or not message.strip():
            continue
            
        role = "user" if i % 2 == 0 else "assistant" 
        api_messages.append({"role": role, "content": message})
    
    # If the last message is from the assistant, remove it (shouldn't happen)
    if len(api_messages) > 0 and api_messages[-1]["role"] == "assistant":
        api_messages.pop()
    
    # Make sure we have valid messages - should be at least one user message
    if not api_messages or not any(msg["role"] == "user" for msg in api_messages):
        # Use the selection message as default
        api_messages = [{"role": "user", "content": selection_message}]
    
    # Build the system prompt from our template
    system_prompt = INPUT_GATHERING_PROMPT
    
    # Call the Anthropic API with function calling enabled
    response = client.messages.create(
        model=model,
        max_tokens=350,
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
                        },
                        "current_savings": {
                            "type": "number",
                            "description": "Optional: Current amount already saved towards the goal"
                        }
                    },
                    "required": ["goal_amount", "time_frame_months"]
                }
            }
        ]
    )
    
    # Debug print statements
    print("Response content:", response.content)
    print("Response content type:", type(response.content))
    print("Content length:", len(response.content))

    # Properly check each content block
    for i, block in enumerate(response.content):
        print(f"\nBlock {i} type:", type(block))
        print(f"Block {i} class name:", block.__class__.__name__)
        
        # Check if this is a ToolUseBlock
        if block.__class__.__name__ == "ToolUseBlock":
            print(f"TOOL CALL FOUND in block {i}:")
            print(f"  Tool name: {block.name}")
            print(f"  Tool input: {block.input}")
    
    # Check for and handle any function calls in the response
    function_results = None
    
    for block in response.content:
        if block.__class__.__name__ == "ToolUseBlock":
            function_results = handle_function_calls(block)
            break
    
    # If there are function results, immediately redirect to graph without further API calls
    if function_results:
        # Store the HTML visualization for later use
        if function_results[0]["function_name"] == "calculate_savings_plan":
            latest_plan_visualization = function_results[0]["result"]
        
        # Add hidden messages to the form
        hidden_messages = [Hidden(m, name="messages") for m in messages]
        
        # Add a success message to the chat history
        success_message = "Your savings plan has been created successfully!"
        messages.append(success_message)
        
        # Create a response that will be displayed in the chat history first
        # before redirecting to the Goal Plan tab
        return (
            ChatMessage(selection_message, True),
            ChatMessage(success_message, False),
            *hidden_messages,
            ChatInput(),
            Raw("""
            <script>
                // Reset any existing form state first
                document.querySelector('#msg-input').value = '';
                
                // Wait a short moment before switching tabs to ensure the message is displayed
                setTimeout(function() {
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', '/tab/goal_plan');
                    xhr.onload = function() {
                        if (xhr.status === 200) {
                            document.getElementById('app-content').outerHTML = xhr.responseText;
                            // Update tab appearance
                            document.querySelectorAll('button').forEach(function(btn) {
                                if (btn.textContent.trim() === 'Goal Plan') {
                                    btn.classList.add('bg-blue-600', 'text-white');
                                    btn.classList.remove('bg-gray-100', 'text-gray-700');
                                } else if (btn.textContent.trim() === 'Goal Setting') {
                                    btn.classList.add('bg-gray-100', 'text-gray-700');
                                    btn.classList.remove('bg-blue-600', 'text-white');
                                }
                            });
                        }
                    };
                    xhr.send();
                }, 500);
            </script>
            """)
        )
    
    # If no function calls, continue with normal text response processing
    # Get the text response (find the first TextBlock)
    r = ""
    for block in response.content:
        if block.__class__.__name__ == "TextBlock":
            r = block.text
            break
    
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
    
    # Add option buttons if found
    if options:
        response_elements.append(OptionButtons(options))
    
    return tuple(response_elements)

# Add an endpoint to serve the dashboard HTML file
@app.get("/dashboard")
def serve_dashboard():
    """View details of the financial goal in an interactive dashboard"""
    try:
        with open("./dashboard_filled.html", "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        # If the file doesn't exist, generate a default dashboard
        # Get the single goal if it exists
        all_goals = load_goals()
        if all_goals:
            goal = all_goals[0]
            goal_amount = goal["goal_amount"]
            time_frame_months = goal["time_frame_months"]
            current_savings = goal.get("current_savings", 0)
            monthly_savings = goal["monthly_savings"]
            
            # Generate a new dashboard
            dashboard_html = generate_dashboard(
                goal="Saving Plan",
                duration=time_frame_months,
                amount=goal_amount
            )
            
            # Save it to file
            with open("./dashboard_filled.html", "w") as file:
                file.write(dashboard_html)
                
            return HTMLResponse(content=dashboard_html)
        else:
            # No goal found, return a simple message
            return HTMLResponse(content="""
            <html>
            <head>
                <title>No Dashboard Available</title>
                <style>
                    body {
                        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f9fafb;
                        color: #111827;
                    }
                    .container {
                        text-align: center;
                        padding: 2rem;
                        background-color: white;
                        border-radius: 0.5rem;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        max-width: 500px;
                    }
                    h1 {
                        font-size: 1.5rem;
                        margin-bottom: 1rem;
                    }
                    p {
                        margin-bottom: 1.5rem;
                        color: #4b5563;
                    }
                    .button {
                        padding: 0.5rem 1rem;
                        background-color: #2563eb;
                        color: white;
                        border-radius: 0.375rem;
                        text-decoration: none;
                        font-weight: 500;
                        transition: background-color 0.2s;
                    }
                    .button:hover {
                        background-color: #1d4ed8;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>No Dashboard Available</h1>
                    <p>Please create a goal first in the application.</p>
                    <a href="/" class="button">Return to App</a>
                </div>
            </body>
            </html>
            """)

# The main screen - entry point of the application
@app.get
def index():
    # Check if we have any saved goals when the app starts
    all_goals = load_goals()
    if all_goals:
        # Display a notification that we've loaded saved goals
        notification = Raw("""
        <div class="fixed bottom-4 right-4 bg-blue-100 border border-blue-300 text-blue-800 px-4 py-3 rounded shadow-md" role="alert" id="notification">
            <div class="flex items-center">
                <div class="py-1"><svg class="h-6 w-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg></div>
                <div>
                    <p class="font-bold">Goal loaded!</p>
                    <p class="text-sm">Your saved goal has been loaded. (Demo Mode)</p>
                </div>
                <div class="ml-4">
                    <button onclick="this.parentElement.parentElement.remove()" class="text-blue-600 hover:text-blue-800 transition-colors">✕</button>
                </div>
            </div>
        </div>
        <script>
            setTimeout(function() {
                document.getElementById('notification').remove();
            }, 5000);
        </script>
        """)
    else:
        notification = ""
    
    page = Div(cls="flex flex-col h-screen")(
        # Header (only include once at the top)
        Div(cls="py-4 border-b border-gray-200 bg-white")(
            Div(cls="text-center")(
                Div("Financial Goal Planner", cls="text-xl font-bold text-blue-600"),
                Div("Plan your financial goals with AI assistance", cls="text-sm text-gray-600 mt-1")
            )
        ),
        # Tabs navigation
        handle_tab_switch(active_tab="goal_setting"),
        # Load the Goal Setting tab content directly
        tab_goal_setting(),
        # Add the notification if we have one
        notification
    )
    return Titled('Financial Goal Planner', page)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Financial Goal Planner')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    args = parser.parse_args()
    
    serve(port=args.port)
else:
    serve()