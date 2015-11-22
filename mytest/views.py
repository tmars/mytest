#coding=utf8
import json
import datetime
import time
import re

from django.template import Context, Template, loader
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms

from models import *

class MessageForm(forms.Form):
    content = forms.CharField(label=u'Содержание', widget=forms.Textarea, max_length=1000)

def get_timestamp(d):
    return int(time.mktime(d.timetuple()))

def parse_message(msg):
    msg = msg.lower()
    if not msg.startswith(u'бот, '):
        return False
    msg = msg[5:]

    url_p = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    patterns = {
        'get_title': u'дай мне заголовок сайта (%s)' % url_p,
        'get_h1': u'дай мне h1 с сайта (%s)' % url_p,
        'save': u'сохрани для меня информацию (.*)',
        'remind': u'напомни мне (.*) через (\d+) (секунд|минут)',
        'get_titles': u'дай мне все варианты заголовков с сайтов ((%s,)%s)' % (url_p, url_p),
    }

    for k,p in patterns.iteritems():
        r = re.match(p, msg)
        if r:
            return k, r.groups()

    return None

def exec_message(msg):
    if not msg:
        return None

    mode, args = msg
    if mode == 'remind':
        content, val, mode = args
        m = Message()
        m.content = u'Напоминаю: %s' % content
        m.author = 'Бот'
        if mode == u'секунд':
            ss = int(val)
        elif mode == u'минут':
            ss = int(val) * 60
        m.created_at = timezone.now() + datetime.timedelta(seconds=ss)
        m.save()
        return m.id

def home(request):
    if 'name' not in request.session:
        return redirect('auth')

    form = MessageForm()
    qs = Message.objects.all().order_by('-created_at')
    ms = list(qs[:5:-1])

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

        msg = parse_message(m.content)
        pk = exec_message(msg)

        return HttpResponse(json.dumps({
            'status': 'success',
            'pk': pk,
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
    
    qs = Message.objects \
        .filter(created_at__gt=d, created_at__lt=timezone.now())
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