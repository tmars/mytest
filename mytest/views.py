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
        'save': u'сохрани для меня информацию\s*(.*)',
        'show': u'дай мне информацию (\d+)',
        'remind': u'напомни мне (.*) через (\d+) (секунд|минут)',
        'get_titles': u'дай мне все варианты заголовков с сайтов ((%s,)%s)' % (url_p, url_p),
    }

    for k,p in patterns.iteritems():
        r = re.match(p, msg)
        if r:
            return k, r.groups()

    return None

def exec_message(request, obj):
    msg = parse_message(obj.content)

    if msg == False:
        return False

    if msg == None:
        m = Message()
        m.content = u'КОМАНДА НЕ РАСПОЗНАНА'
        m.session_key = request.session.session_key
        m.author = u'Бот'
        m.save()
        return None

    mode, args = msg
    if mode == 'remind':
        content, val, mode = args
        m = Message()
        m.content = u'Напоминаю: %s' % content
        m.session_key = request.session.session_key
        m.author = u'Бот'
        if mode == u'секунд':
            ss = int(val)
        elif mode == u'минут':
            ss = int(val) * 60
        m.created_at = timezone.now() + datetime.timedelta(seconds=ss)
        m.save()
    
    elif mode == 'save':
        if args[0]:
            # Если информация ВВЕДЕНА, то сохраняем ее и выводим ID
            i = Info()
            i.content = args[0]
            i.save()

            m = Message()
            m.content = u'Иформация сохранена с ID=%d' % i.id
            m.session_key = request.session.session_key
            m.author = u'Бот'
            m.save()

        else:
            # Если информация не введена
            # смотрим предыдущее сообщение c задачей
            # сохраняем результат задачи и выводим ID
            qs = Message.objects \
                .filter(created_at__lt=obj.created_at, task__isnull=False) \
                .order_by('-created_at')
            if qs.count() == 0:
                m = Message()
                m.content = u'Иформация для сохранения не определена'
                m.session_key = request.session.session_key
                m.author = u'Бот'
                m.save()

            t = qs[0].task
            r = ''
            if t.command == 'get_titles':
                try:
                    rs = json.loads(t.results)
                    r = ',<br>'.join(['"%s"="%s"' % (k,v) for k,v in rs.iteritems()])
                except:
                    pass

            i = Info()
            i.content = '%s, %s' % (t.created_at, r)
            i.save()

            m = Message()
            m.content = u'Иформация сохранена с ID=%d' % i.id
            m.session_key = request.session.session_key
            m.author = u'Бот'
            m.save()

    elif mode == 'show':
        i = None
        try:
            i = Info.objects.get(pk=args[0])
        except:
            pass

        if not i:
            m = Message()
            m.content = u'Иформация с ID=%s не найдена' % args[0]
            m.session_key = request.session.session_key
            m.author = u'Бот'
            m.save()
        else:
            m = Message()
            m.content = u'Иформация с ID=%s : %s' % (i.id, i.content)
            m.session_key = request.session.session_key
            m.author = u'Бот'
            m.save()
            
    elif mode == 'get_title':
        t = Task.create(mode, {'url': args[0]}, request.session.session_key)
        t.run()
        obj.task = t
        obj.save()

    elif mode == 'get_h1':
        t = Task.create(mode, {'url': args[0]}, request.session.session_key)
        t.run()
        obj.task = t
        obj.save()

    elif mode == 'get_titles':
        t = Task.create(mode, {'urls': args[0]}, request.session.session_key)
        t.run()
        obj.task = t
        obj.save()

def home(request):
    if 'name' not in request.session:
        return redirect('auth')
    
    form = MessageForm()
    qs = Message.objects \
        .filter(session_key=request.session.session_key) \
        .order_by('-created_at')
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
        m.session_key = request.session.session_key
        m.save()

        exec_message(request, m)

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
    
    qs = Message.objects.filter(
        created_at__gt=d, 
        created_at__lt=timezone.now(),
        session_key=request.session.session_key
    )
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