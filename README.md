# FinnaGetit - Financial Goal Planner
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> FinnaGetit is a modern, AI-powered financial goal planning application that helps users set, track, and achieve their financial goals through intelligent conversation and interactive visualizations.

## 📸 Screenshots

*Coming soon*

## ✨ Features

- **Conversational Goal Setting**: Chat with an AI assistant to define financial goals in natural language
- **Smart Cost Estimation**: The AI helps estimate the cost of various goals based on user input
- **Interactive Dashboard**: Visual representation of savings progress and timeline
- **Goal Management**: Save, view, and delete multiple financial goals
- **Personalized Savings Plans**: Get customized monthly savings targets based on goal amount and timeframe

## 🛠️ Technology Stack

- **Frontend**: FastHTML, Tailwind CSS, HTMX for dynamic interactions
- **Backend**: Python
- **AI**: Anthropic Claude API (Claude 3.5 Sonnet model)
- **Visualization**: Custom dashboard with interactive elements
- **Data Storage**: Local JSON-based storage for goals

## 🚀 Setup

### Prerequisites

- Python 3.7+
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FinnaGetit.git
   cd FinnaGetit
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # For Mac/Linux
   python -m venv venv
   source venv/bin/activate
   
   # For Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install fasthtml anthropic
   ```

### Environment Variables

Before running the application, you need to set up the Anthropic API key:

**For Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**For Windows (Command Prompt):**
```bash
set ANTHROPIC_API_KEY=your-api-key-here
```

**For Windows (PowerShell):**
```bash
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

### Permanent Setup

To avoid setting the environment variable each time:

**For Mac/Linux:**
Add to your `~/.bashrc`, `~/.zshrc`, or equivalent:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**For Windows:**
Set a permanent environment variable through System Properties:
1. Search for "Environment Variables" in the Start menu
2. Click "Edit the system environment variables"
3. Click the "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `ANTHROPIC_API_KEY`
6. Variable value: your API key
7. Click "OK" to save

Alternatively, you can modify the `config.py` file:
```python
ANTHROPIC_API_KEY = "your-api-key-here"
```

## 🏃‍♂️ Running the Application

Start the application with:

```bash
python goal_setting.py
```

## 📖 How to Use

1. **Setting a Goal**: 
   - Navigate to the "Goal Setting" tab
   - Start a conversation with the AI by describing your financial goal
   - The AI will ask relevant questions to understand your needs
   - Answer the questions or select from provided options
   - Once enough information is gathered, a savings plan will be generated

2. **Viewing Goals**:
   - Switch to the "My Goals" tab to see all your saved goals
   - Click "View Details" to get in-depth information about a specific goal
   - Click "Open Interactive Dashboard" for a full-screen visualization

3. **Managing Goals**:
   - Delete unwanted goals using the delete button
   - Create new goals by navigating back to the "Goal Setting" tab

## 🌟 Example Workflow

1. User: "I want to save for a trip to Japan next year"
2. AI: "Great! How long are you planning to stay in Japan?"
   Options: 1 week | 2 weeks | 1 month | Longer
3. User: *selects "2 weeks"*
4. AI: "What's your estimated budget for this trip?"
   Options: Budget ($3,000) | Standard ($5,000) | Luxury ($8,000) | Custom
5. User: *selects "Standard ($5,000)"*
6. AI: *generates savings plan with monthly targets*
7. System: *displays interactive visualization and automatically switches to the "My Goals" tab*

## 📁 Project Structure

- `goal_setting.py`: Main application file with UI and business logic
- `prompts.py`: Contains prompt templates for the AI assistant
- `goal_storage.py`: Handles saving and loading goals
- `dashboard.py`: Generates interactive dashboard visualizations
- `theme.py`: Contains styling information
- `config.py`: Configuration for API keys

## 🔮 Future Enhancements

- Integration with banking APIs for real-time financial data
- Multi-currency support
- Advanced financial projections and what-if scenarios
- Mobile application version
- Export functionality for savings plans

## ❓ Troubleshooting

### Common Issues

- **API Key not recognized**: Ensure your Anthropic API key is correctly set up in your environment variables or `config.py` file.
- **ImportError**: Make sure all dependencies are installed by running `pip install fasthtml anthropic`.
- **Application not starting**: Check that you're using Python 3.7 or newer.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Anthropic](https://www.anthropic.com/) for their powerful Claude API
- [FastHTML](https://fasthtml.org/) for the frontend framework
- All contributors who have helped make this project better
