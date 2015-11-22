#coding=utf8
import json
import datetime
import time

from django.template import Context, Template, loader
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms

from models import *

class MessageForm(forms.Form):
    content = forms.CharField(label=u'Содержание', widget=forms.Textarea, max_length=1000)

def get_timestamp(d):
    return int(time.mktime(d.timetuple()))

def home(request):
    if 'name' not in request.session:
        return redirect('auth')

    form = MessageForm()
    qs = Message.objects.all()
    ms = list(qs)

    ts = 0
    if len(ms):
        ts = get_timestamp(ms[-1].created_at)

    return render(request, 'mytest/home.html', {
        'form': form,
        'list': ms,
        'ts': ts,
    })

def auth(request):
    class AuthForm(forms.Form):
        name = forms.CharField(label=u'Ваше имя', max_length=30, min_length=2)

    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            return redirect('home')
    else:
        form = AuthForm()

    return render(request, 'mytest/auth.html', {
        'form': form,    
    })

def ajax_put_message(request):
    if 'name' not in request.session:
        return HttpResponse(json.dumps({
            'status': 'error',
            'error': 'not auth',
        }))

    form = MessageForm(request.POST)
    if form.is_valid():
        
        m = Message()
        m.content = form.cleaned_data['content']
        m.author = request.session['name']
        m.save()

        return HttpResponse(json.dumps({
            'status': 'success',    
        }))

    else:
        return HttpResponse(json.dumps({
            'status': 'error',
            'error': 'error form',
        }))

def ajax_get_messages(request):
    ts = request.GET.get('ts')

    try:
        d = datetime.datetime.fromtimestamp(float(ts))
    except:
        return HttpResponse(json.dumps({
            'status': 'error',
            'error': 'not timestamp',
        }))
    
    qs = Message.objects.filter(created_at__gt=d)
    ms = list(qs)
    content = ''

    if len(ms):
        t = loader.get_template('mytest/messages.html')
        c = Context({'list': qs})
        content = t.render(c)
        ts = get_timestamp(ms[-1].created_at)

    return HttpResponse(json.dumps({
        'status': 'success',
        'content': content,
        'ts': ts,
    }))