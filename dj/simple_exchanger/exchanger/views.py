# exchange/views.py
import os
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Helper function to load the last 10 text entries from the history file
def load_text_history():
    if os.path.exists(settings.HISTORY_FILE):
        with open(settings.HISTORY_FILE, 'r') as file:
            history = json.load(file)
    else:
        history = []
    return history[-10:][::-1]  # Last 10 entries in reverse order

# View to handle index
def index(request):
    files = os.listdir(settings.MEDIA_ROOT)
    text_history = load_text_history()
    latest_text = text_history[0] if text_history else ""
    return render(request, 'index.html', {'files': files, 'latest_text': latest_text, 'text_history': text_history, 'MEDIA_URL': settings.MEDIA_URL })

# View to handle file upload and text submission
def upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            fs = FileSystemStorage()
            fs.save(file.name, file)
        elif 'shared_text' in request.POST:
            new_text = request.POST['shared_text']
            history = load_text_history()
            history.append(new_text)
            with open(settings.HISTORY_FILE, 'w') as file:
                json.dump(history, file)
        return redirect('index')
    return redirect('index')

# View to delete files
def delete_file(request):
    filename = request.POST.get('filename')
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return JsonResponse({'success': True})

# View to get specific text entry from history
def get_text_history(request):
    index = int(request.POST.get('index', 0))
    text_history = load_text_history()
    if 0 <= index < len(text_history):
        return JsonResponse({'text': text_history[index]})
    return JsonResponse({'text': ''})
