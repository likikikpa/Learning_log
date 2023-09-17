from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from . models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.http import Http404

# Create your views here.


def index(request):
    """Домашняя страница приложения learning_log"""
    return render(request, "learning_logs/index.html")

@login_required
def topics(request):
    # Выводит список тем
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Выводит одну тему и все ее записи"""
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(request, topic)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Oпределяет новую тему """
    if request.method != 'POST':
        """ Данные не отпровлялись; создается пустая форма """
        form = TopicForm()
    else:
        """ отправленные данные POST, обработать данные"""
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    # Вывести пустую или не действительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме """
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(request, topic)
    if request.method != 'POST':
        """Данные не отправлялись; создается пустая форма"""
        form = EntryForm()
    else:
        """Отправлены данные POST; обработать данные"""
        form = EntryForm(data=request.POST)
        if form.is_valid:
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    # Вывести пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_Logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)
    if request.method != 'POST':
        """ Исходный запрос; форма заполняется данными текущей записи """
        form = EntryForm(instance=entry)
    else:
        """Отправка данных POST; обработать данные"""
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid:
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'topic': topic, 'entry': entry, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


# Рефракторинг
def check_topic_owner(request, topic):
    if topic.owner != request.user:
        raise Http404