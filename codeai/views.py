import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key for Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-1.0-flash')

# Task-specific prompts
TASK_PROMPTS = {
    "Code Review": "Please review this code and suggest improvements:",
    "Debug Help": "Help me find and fix bugs in this code:",
    "Code Explanation": "Please explain how this code works:",
    "Best Practices": "What are the best practices for this code:",
    "Code Generation": "Please generate a code snippet for this task:"
}

def index(request):
    if request.method == 'POST':
        task_type = request.POST.get('task_type')
        user_input = request.POST.get('user_input')

        if not user_input.strip():
            return JsonResponse({'error': 'Input cannot be empty. Please provide code or a detailed description.'})

        try:
            # Create a prompt for the AI
            prompt = f"""{TASK_PROMPTS[task_type]}
            
            Input:
            {user_input}
            
            Provide a detailed and structured response."""

            # Generate response using Gemini AI model
            response = model.generate_content(prompt)
            result = response.text
            result = result.replace("*"," ")
            

            # Save the request history (optional)
            request.session.setdefault('code_history', []).append({
                "task": task_type,
                "input": user_input,
                "output": result
            })
            request.session.modified = True

            # Pass the index of the latest response to the result page
            return redirect('codeai:show_response', idx=len(request.session['code_history']) - 1)

        except Exception as e:
            return JsonResponse({'error': f"An error occurred: {e}"})

    return render(request, 'codeai/index.html', {
        'task_types': TASK_PROMPTS.keys(),
        'history': request.session.get('code_history', [])
    })


def show_response(request, idx):
    # Ensure idx is an integer and valid
    try:
        idx = int(idx)
        history = request.session.get('code_history', [])
        if 0 <= idx < len(history):
            entry = history[idx]
            task = entry['task']
            user_input = entry['input']
            response = entry['output']
            return render(request, 'codeai/show_response.html', {
                'task': task,
                'input': user_input,
                'response': response,
                'idx': idx  # Pass idx so you can use it in the download link
            })
    except (ValueError, IndexError):
        return redirect('codeai:index')  # Redirect if invalid idx is passed

    return redirect('codeai:index')  # Default to redirect if no valid idx is found

def download_response_mdeol(request, idx):
    history = request.session.get('code_history', [])
    if 0 <= idx < len(history):
        response_text = history[idx]['output']
        response = HttpResponse(response_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={history[idx]["task"].lower().replace(" ", "_")}_response.txt'
        return response
    return JsonResponse({'error': 'Invalid history index'})

def download_response(request, idx):
    history = request.session.get('code_history', [])
    if 0 <= idx < len(history):
        response_text = history[idx]['output']
        response = HttpResponse(response_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={history[idx]["task"].lower().replace(" ", "_")}_response.txt'
    return JsonResponse({'error': 'Invalid history index'})
