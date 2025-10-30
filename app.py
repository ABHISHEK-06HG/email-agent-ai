from flask import Flask, request, jsonify
from main import build_graph

app = Flask(__name__)

@app.route('/process_email', methods=['POST'])
def process_email():
    data = request.get_json()
    email_content = data.get('email_content')

    if not email_content:
        return jsonify({'error': 'No email_content provided'}), 400

    graph = build_graph()
    initial_state = {
        "email_content": email_content,
        "email_id": "frontend_email",  # A placeholder ID for frontend emails
        "summary": "",
        "intent": "",
        "messages": [],
        "meeting_details": {},
        "meeting_scheduled": False,
        "schedule_response": ""
    }
    
    # Invoke the graph with the email content
    final_state = graph.invoke(initial_state)

    return jsonify(final_state)

if __name__ == '__main__':
    app.run(debug=True, port=5000)