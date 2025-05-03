modern_theme = """
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'primary': '#2563EB',
        'primary-dark': '#1D4ED8',
        'primary-light': '#DBEAFE',
        'secondary': '#059669',
        'neutral-dark': '#111827',
        'neutral-medium': '#4B5563',
        'neutral-light': '#F3F4F6',
        'user-bubble': '#DBEAFE',
        'assistant-bubble': '#F9FAFB',
        'input-bg': '#FFFFFF',
        'input-text': '#111827',
        'card-border': '#E5E7EB'
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      },
      boxShadow: {
        'soft': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'medium': '0 4px 6px rgba(0, 0, 0, 0.1)'
      }
    }
  }
}
</script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #F9FAFB;
  color: #111827;
  line-height: 1.5;
}

/* Chat bubbles */
.chat-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.bg-user-bubble {
  background-color: #DBEAFE;
  color: #1E40AF;
}

.bg-assistant-bubble {
  background-color: #FFFFFF;
  border: 1px solid #E5E7EB;
  color: #111827;
}

/* Tabs */
.tab-active {
  background-color: #2563EB;
  color: white;
  font-weight: 600;
  border-radius: 0.5rem;
}

.tab-inactive {
  background-color: #F3F4F6;
  color: #4B5563;
  border-radius: 0.5rem;
}

.tab-inactive:hover {
  background-color: #E5E7EB;
}

/* Input field - ensure text is visible */
#msg-input {
  background-color: white;
  color: #111827;
  border-color: #D1D5DB;
}

#msg-input::placeholder {
  color: #9CA3AF;
}

/* Chat area scrollbar */
#chatlist::-webkit-scrollbar {
  width: 6px;
}

#chatlist::-webkit-scrollbar-track {
  background: #F3F4F6;
}

#chatlist::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 6px;
}

/* Card styles */
.card {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Simple animation for typing indicator */
.typing-indicator span {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: #9CA3AF;
  margin: 0 1px;
  animation: bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
}

/* Fix for notification visibility */
#notification {
  background-color: #DBEAFE;
  color: #1E40AF;
  border-color: #2563EB;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
"""