from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import MatchBasic, Stat, Summoner, Streak
from .forms import NameForm
from riotwatcher import LolWatcher, ApiError


api_key = ''
watcher = LolWatcher(api_key)
my_region = 'na1'

# Create your views here.
def index(request):
    basic = MatchBasic.objects.all()
    context = {'basic':basic}
    return render(request, 'search/index.html', context)

def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            sums = Summoner.objects.all()
            mat = MatchBasic.objects.all()
            sta = Stat.objects.all()
            strk = Streak.objects.all()
            sums.delete()
            mat.delete()
            sta.delete()
            strk.delete()
            name = Summoner()
            name.summonerName = form.cleaned_data['summonerName']
            name.save()
            account = name.getId()
            matches = name.getMatches(account)
            matches.getWLStreak()
            
            return HttpResponseRedirect(name.summonerName)
    else:
        form = NameForm()
            
            
    
    
    return render(request, 'search/name.html', {'form' : form})

def get_stats(request, summonerName):
    user = watcher.summoner.by_name(my_region, summonerName)
    enId = user['accountId']
    summon = summonerName
    matbase = MatchBasic.objects.filter(encrypt_id = enId)
    strk = Streak.objects.filter(encrypt_id = enId)
    sta = Stat.objects.filter(encrypt_id = enId)
    win = Stat.objects.filter(win = True, encrypt_id = enId).count()
    lose = Stat.objects.filter(win = False, encrypt_id = enId).count()
    context = {'matbase': matbase, 'strk': strk, 'sta':sta, 'summon': summon, 'win':win, 'lose':lose}
    return render(request, 'search/stats.html', context)