from django.db import models
from riotwatcher import LolWatcher, ApiError
from django.contrib.postgres.fields import ArrayField
import datetime
import pandas as pd
import time
import psycopg2



api_key = 'RGAPI-283d6ae5-b6cd-4cd3-87d8-3f5021ad92c2'
watcher = LolWatcher(api_key)
my_region = 'na1'
currTime = round(time.time())
twelveHours = currTime-86400

class Summoner(models.Model):
    summonerName = models.CharField(max_length = 30)
    
    def __str__(self):
        return self.summonerName

    def getId(self):
        user = watcher.summoner.by_name(my_region, self.summonerName)
        Id = user['accountId']
        return Id
    
    def getMatches(self, encrypt):
        matches = watcher.match.matchlist_by_account(my_region, encrypt, begin_time =twelveHours*1000, end_time = currTime*1000)
        matchList = matches['matches']
        champ = []
        timeSinceMatch = []
        matchids = []
        for match in matchList:
            timeSinceMatch.append(round(round(currTime - (match['timestamp']/1000))/3600))
            matchids.append(match['gameId'])
        matbase = MatchBasic()
        matbase.matchId = matchids
        matbase.timeofMatch = timeSinceMatch
        matbase.encrypt_id = encrypt
        #matbase.save()
        return matbase

class MatchBasic(models.Model):
    matchId = ArrayField(models.CharField(max_length=100))
    timeofMatch = ArrayField(models.CharField(max_length=50))
    encrypt_id = models.CharField(max_length=50)

    #def __str__(self):
        #return {"matchId": self.matchId, "timeofMatch": self.timeofMatch }
    
    def getWLStreak(self):
        total = []
        latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
        static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
        champ_dict = {}

        for key in static_champ_list['data']:
            row = static_champ_list['data'][key]
            champ_dict[row['key']] = row['id']

        for matches in self.matchId:
            match = watcher.match.by_id(my_region, matches)
            
            partID = match['participantIdentities']
            
            myId = 0
            me = Stat()
            
            
            for participant in partID:
                
                if self.encrypt_id == participant['player']['accountId']:
                    myId = participant['participantId']-1
                    me.championId = match['participants'][myId]['championId']
                    me.champLevel = match['participants'][myId]['stats']['champLevel']
                    me.championName = champ_dict[str(me.championId)]
                    me.win = match['participants'][myId]['stats']['win']
                    me.kills = match['participants'][myId]['stats']['kills']
                    me.deaths = match['participants'][myId]['stats']['deaths']
                    me.assists = match['participants'][myId]['stats']['assists']
                    me.totalMinionsKilled = match['participants'][myId]['stats']['totalMinionsKilled']
                    me.goldEarned = match['participants'][myId]['stats']['goldEarned']
                    me.spell1 = match['participants'][myId]['spell1Id']
                    me.spell2 = match['participants'][myId]['spell2Id']
                    me.encrypt_id = self.encrypt_id
                    me.save()
                    total.append(me.win)
                    break
        streak = 0
        longestStreak = 0
        prev = total[0]
        wins = Streak()
        wins.typeofStreak = prev
        wins.encrypt_id = self.encrypt_id
        for match in total:
            if match == prev:
                streak = streak + 1
                prev = match
                if streak > longestStreak:
                    longestStreak = streak
            else:
                break
        
        
       
        wins.streakLength = longestStreak
        wins.save()
        
            
            
            
            
class Streak(models.Model):
    encrypt_id = models.CharField(max_length=50)
    streakLength = models.CharField(max_length = 10)
    typeofStreak = models.CharField(max_length = 10)    

    def __str__(self):
        return '%s %s' % (self.streakLength, self.typeofStreak)      
            

        

class Stat(models.Model):
    championId =models.CharField(max_length=50)
    championName=models.CharField(max_length=50)
    champLevel=models.CharField(max_length=50)
    win =models.CharField(max_length=50)
    kills=models.CharField(max_length=50)
    deaths =models.CharField(max_length=50)
    assists =models.CharField(max_length=50)
    totalMinionsKilled=models.CharField(max_length=50)
    goldEarned=models.CharField(max_length=50)
    spell1=models.CharField(max_length=50)
    spell2=models.CharField(max_length=50)
    encrypt_id = models.CharField(max_length=50)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s ' % (self.championId, self.championName, self.champLevel, 
        self.deaths, self.encrypt_id, self.goldEarned, self.kills, self.spell1, self.spell2, self.totalMinionsKilled, self.win)
