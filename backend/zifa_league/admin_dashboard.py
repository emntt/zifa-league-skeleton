from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import path
from teams.models import Team
from players.models import Player
from matches.models import Match
from discipline.models import Discipline
from injuries.models import Injury
from standings.models import Standing
from transfers.models import Transfer

@staff_member_required
def league_dashboard(request):
    team_count = Team.objects.count()
    player_count = Player.objects.count()
    match_count = Match.objects.count()
    injury_count = Injury.objects.count()
    transfer_count = Transfer.objects.count()
    # Goals per team (top 10)
    goals_per_team = (
        Match.objects.values('home_team__name')
        .annotate(goals_home_sum=models.Sum('score_home'))
        .order_by('-goals_home_sum')[:10]
    )
    # Cards per month
    from django.db.models.functions import TruncMonth
    cards_per_month = (
        Discipline.objects.annotate(month=TruncMonth('date'))
        .values('month', 'type')
        .annotate(count=models.Count('id'))
    )
    # Standings points (top 10)
    standings = Standing.objects.select_related('team').order_by('-points')[:10]
    # Transfers per month
    transfers_per_month = (
        Transfer.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=models.Count('id'))
    )
    # Injuries per team (top 10)
    injuries_per_team = (
        Injury.objects.values('player__team__name')
        .annotate(count=models.Count('id'))
        .order_by('-count')[:10]
    )
    # Matches per venue (top 10)
    matches_per_venue = (
        Match.objects.values('venue__name')
        .annotate(count=models.Count('id'))
        .order_by('-count')[:10]
    )
    return render(request, "admin/league_dashboard.html", {
        "team_count": team_count,
        "player_count": player_count,
        "match_count": match_count,
        "injury_count": injury_count,
        "transfer_count": transfer_count,
        "goals_per_team_labels": [g['home_team__name'] for g in goals_per_team],
        "goals_per_team_values": [g['goals_home_sum'] for g in goals_per_team],
        "cards_per_month_data": list(cards_per_month),
        "standings_labels": [s.team.name for s in standings],
        "standings_values": [s.points for s in standings],
        "transfers_months": [str(t['month'])[:7] for t in transfers_per_month],
        "transfers_counts": [t['count'] for t in transfers_per_month],
        "injuries_team_labels": [i['player__team__name'] for i in injuries_per_team],
        "injuries_team_values": [i['count'] for i in injuries_per_team],
        "matches_venue_labels": [m['venue__name'] for m in matches_per_venue],
        "matches_venue_counts": [m['count'] for m in matches_per_venue],
    })

def get_admin_urls(urls):
    def get_urls():
        return [path('league-dashboard/', league_dashboard, name='league-dashboard')] + urls
    return get_urls

from django.contrib import admin
admin.site.get_urls = get_admin_urls(admin.site.get_urls())