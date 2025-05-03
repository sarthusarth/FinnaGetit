def calculate_savings_plan(goal_amount, time_frame_months, current_savings=0):
    print(f"calculate_savings_plan called with: goal_amount={goal_amount}, time_frame_months={time_frame_months}, current_savings={current_savings}")
    """Calculate the required monthly savings to reach a     financial goal and return FastHTML visualization"""
    #generate_dashboard(goal="savings", goal_amount=goal_amount, time_frame_months=time_frame_months, current_savings=current_savings)
    
    try:
        # Convert inputs to float/int if they're not already
        goal_amount = float(goal_amount)
        time_frame_months = int(time_frame_months)
        current_savings = float(current_savings)
        
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
        
        # Save the goal to persistent storage
        goal_data = {
            "goal_amount": goal_amount,
            "time_frame_months": time_frame_months,
            "current_savings": current_savings,
            "monthly_savings": monthly_savings
        }
        save_goal(goal_data)
        
        # For the purpose of simply generating the graph and redirecting, we just need to return
        # a simple success flag
        return {
            "visualization_ready": True
        }
    except Exception as e:
        print(f"Error in calculate_savings_plan: {str(e)}")
        # Return a minimal result so the app doesn't crash
        return {
            "error": str(e),
            "visualization_ready": False
        }

def generate_savings_graph(months, savings_progression, scaled_values, graph_height, goal_amount, monthly_savings, time_frame_months, current_savings):
    """Generate FastHTML code for a savings growth visualization"""
    # Create a responsive container for the chart
    container = Div(cls="w-full bg-white rounded-lg shadow border border-gray-200 p-5 mb-4")
    
    # Chart title and summary
    container(
        Div(cls="text-lg font-semibold mb-2 text-gray-900")("Savings Growth Projection"),
        Div(cls="text-sm text-gray-600 mb-4 pb-2 border-b border-gray-200")(
            f"Monthly savings: ${round(monthly_savings, 2)} for {time_frame_months} months to reach ${round(goal_amount, 2)}"
        )
    )
    
    # Graph container
    graph = Div(cls="relative h-64 mt-4")
    
    # Y-axis labels and grid lines
    y_labels = Div(cls="absolute left-0 top-0 bottom-0 w-14 flex flex-col justify-between text-xs text-gray-600")
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
    goal_line = Div(cls="absolute top-0 left-0 right-0 border-t-2 border-dashed border-green-500 flex justify-end")
    goal_line(Div(cls="bg-green-500 text-white text-xs px-1 py-0.5 rounded-sm")("Goal"))
    
    # Chart data visualization - we'll use SVG for the line graph
    chart_svg = Raw(f"""
    <svg class="w-full h-full overflow-visible">
        <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="rgba(37, 99, 235, 0.4)"/>
                <stop offset="100%" stop-color="rgba(37, 99, 235, 0.05)"/>
            </linearGradient>
        </defs>
        
        <!-- Area under the curve -->
        <path d="M{0},{graph_height} {" ".join([f"L{i * (100 / time_frame_months)}%,{graph_height - scaled_values[i]}" for i in range(len(months))])} L{100}%,{graph_height} Z" 
              fill="url(#gradient)" stroke="none" />
              
        <!-- Line graph -->
        <path d="M{0},{graph_height - scaled_values[0]} {" ".join([f"L{i * (100 / time_frame_months)}%,{graph_height - scaled_values[i]}" for i in range(1, len(months))])}" 
              fill="none" stroke="#2563EB" stroke-width="2.5" />
              
        <!-- Data points -->
        {"".join([f'<circle cx="{i * (100 / time_frame_months)}%" cy="{graph_height - scaled_values[i]}" r="4" fill="#2563EB" stroke="white" stroke-width="1" />' for i in range(0, len(months), max(1, time_frame_months // 6))])}
    </svg>
    """)
    
    # X-axis labels
    x_labels = Div(cls="flex justify-between text-xs text-gray-600 mt-2")
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
    metrics = Div(cls="grid grid-cols-2 gap-4 mt-6")
    metrics(
        Div(cls="bg-gray-50 rounded-lg p-4 border border-gray-200")(
            Div(cls="text-xs text-gray-600")("Monthly Savings"),
            Div(cls="text-lg font-semibold text-blue-600")(f"${round(monthly_savings, 2)}")
        ),
        Div(cls="bg-gray-50 rounded-lg p-4 border border-gray-200")(
            Div(cls="text-xs text-gray-600")("Total Goal"),
            Div(cls="text-lg font-semibold text-blue-600")(f"${round(goal_amount, 2)}")
        ),
        Div(cls="bg-gray-50 rounded-lg p-4 border border-gray-200")(
            Div(cls="text-xs text-gray-600")("Time Frame"),
            Div(cls="text-lg font-semibold text-blue-600")(f"{time_frame_months} months")
        ),
        Div(cls="bg-gray-50 rounded-lg p-4 border border-gray-200")(
            Div(cls="text-xs text-gray-600")("Current Savings"),
            Div(cls="text-lg font-semibold text-blue-600")(f"${round(current_savings, 2)}")
        )
    )
    
    container(metrics)
    
    return container
