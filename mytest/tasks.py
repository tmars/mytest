#coding=utf8
import time
from grab import Grab 
from grab.error import GrabCouldNotResolveHostError

def get_title(t, url):
    g = Grab()
    
    try:
        g.go(url)
    except GrabCouldNotResolveHostError:
        t.save_message(u'Сайт не найден')
        return
    except:
        t.save_message(u'Неизвестная ошибка')
        return

    try:
        res = g.doc.select('//title').text()
    except:
        t.save_message(u'Заголовок не найден')
        return 

    if not len(res):
        t.save_message(u'Заголовок пустой')
        return

    t.save_message(res)

def get_h1(t, url):
    g = Grab()

    try:
        g.go(url)
    except GrabCouldNotResolveHostError:
        t.save_message(u'Сайт не найден')
        return
    except:
        t.save_message(u'Неизвестная ошибка')
        return

    try:
        res = g.doc.select('//h1').text()
    except:
        t.save_message(u'H1 не найден')
        return

    if not len(res):
        t.save_message(u'H1 пустой')
        return 

    t.save_message(res)

def get_titles(t, urls):
    g = Grab()
    urls = urls.split(',')

    results = {}
    for url in urls:
        try:
            g.go(url)
        except GrabCouldNotResolveHostError:
            t.save_message(u'Сайт %s не найден' % url)
            continue
        except:
            t.save_message(u'Неизвестная ошибка %s' % url)
            continue

        try:
            res = g.doc.select('//title').text()
            results[url] = res
        except:
            t.save_message(u'Сайт %s заголовок не найден' % url)

    if results:
        t.save_results(results)
        t.save_message(u'Заголовоки %s с сайтов %s' % (
            ','.join(results.values()),
            ','.join(results.keys())
        ))
            