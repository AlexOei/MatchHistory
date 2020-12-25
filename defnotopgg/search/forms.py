from django import forms

class NameForm(forms.Form):
    summonerName = forms.CharField(label = 'Summoner Name', max_length = 30)