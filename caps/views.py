from django.shortcuts import render, get_object_or_404
from .models import Team, Player, Contract, CapHit, RetainedSalary

# Create your views here.

buried_thresholdz = {
    '2022-23': 1125000, '2023-24': 1150000, '2024-25': 1150000, '2026-27': 1150000, '2028-29': 1150000, '2029-30': 1150000, '2030-31': 1150000, '2031-32': 1150000, '2032-33': 1150000,
    }

def calculate_effective_cap_hit(cap_hit_obj, retained_amount=0, season='2025-26'):
    # Active: full cap hit - retained
    # LTIR full cap hit - retained (relief done elsewhere)
    # IR: full cap - retained (no relief)
    # Buried max(cap_hit - buried_threshold, 0) - retained

    base_cap_hit = cap_hit_obj.cap_hit - retained_amount

    if cap_hit_obj.roster_status == 'buried':
        buried_threshold = buried_thresholdz.get(season, 1150000)

        buried_cap_hit = max(base_cap_hit - buried_threshold, 0)
        return buried_cap_hit
    else:
        return base_cap_hit

def home(request):
    teams = Team.objects.all().order_by('division', 'name')
    return render(request, 'caps/home.html', {'teams': teams})

def team_overview(request, abbreviation):
    team = get_object_or_404(Team, abbreviation=abbreviation.upper())
    players = team.players.all().order_by('last_name')

    display_seasons = [ '2025-26', '2026-27', '2027-28', '2028-29', '2029-30', '2030-31']

    forwards = []
    defensemen = []
    goalies = []

    season_totals = {season: 0 for season in display_seasons}

    ltir_pool = 0

    retained_cap_totals = {season: 0 for season in display_seasons}
    for retained in team.retained_contracts.all():
        contract = retained.contract
        if contract.status == 'active' and contract.player.current_team != team:
            for season in display_seasons:
                cap_hit = contract.cap_hits.filter(season=season).first()
                if cap_hit:
                    retained_cap_totals[season] += retained.amount
                    season_totals[season] += retained.amount
                

    for player in players:
        
        player_seasons = {}

        contract_end = None
        free_agent_type = None

        for contract in player.contracts.filter(status__in=['active', 'future']):
            retained = contract.retained_salaries.first()
            
            if retained:
                retained_amount = retained.amount
            else:
                retained_amount = 0
            for season in display_seasons:
                cap_hit = contract.cap_hits.filter(season=season).first()
                if cap_hit:
                    effective_cap_hit = calculate_effective_cap_hit(cap_hit, retained_amount, season)

                    player_seasons[season] = {
                        'cab_hit_obj': cap_hit, 'effective_cap_hit': effective_cap_hit, 'retained_amount': retained_amount, 'roster_status': cap_hit.roster_status,
                    }

                    season_totals[season] += effective_cap_hit

                    if season == '2025-26' and cap_hit.roster_status == 'ltir':
                        ltir_pool += cap_hit.cap_hit - retained_amount
            if contract.end_season:
                if contract_end is None or contract.end_season > contract_end:
                    contract_end = contract.end_season

                    # Update RFA calculation eventually below

                    if contract.is_entry_level:
                        free_agent_type = 'RFA'
                    else:
                        free_agent_type = 'UFA'
        if player_seasons:
            player_data = {
                'player': player,
                'seasons': player_seasons,
                'contract_end': contract_end,
                'free_agent_type': free_agent_type,
            }

            if player.position in ['C', 'LW', 'RW']:
                forwards.append(player_data)
            elif player.position in ['LD', 'RD']:
                defensemen.append(player_data)
            elif player.position == 'G':
                goalies.append(player_data)
    
    
    retained_contracts = []
    
    for retained in team.retained_contracts.all():
        contract = retained.contract

        if contract.status == 'active' and contract.player.current_team != team:
            retained_contracts.append({
                'player': contract.player, 'current_team': contract.player.current_team,
                'retained_amount': retained.amount, 'retention_percentage': retained.retention_percentage,
                'contract_end': contract.end_season
            })

    
    bought_out_contracts = []

    for contract in Contract.objects.filter(status='bought_out'):
        responsible_team = contract.buyout_team if contract.buyout_team else contract.signing_team


        # Oliver Ekman Larsson's Arizona/Utah contract was 12% retained, then traded to VAN and bought out. so they're on the hook for some
        # Pretty sure this is the only contract in the league like that
        retained = contract.retained_salaries.first()

        is_buyout_team = responsible_team == team
        is_retaining_team = (retained and retained.retaining_team ==team)

        if is_buyout_team or is_retaining_team:
            buyout_seasons = {}
            for season in display_seasons:
                cap_hit_obj = contract.cap_hits.filter(season=season).first()
                if cap_hit_obj:
                    full_buyout_cap = cap_hit_obj.cap_hit

                    if retained:
                        retained_pct = float(retained.retention_percentage) / 100
                        # Only retained
                        if is_retaining_team and not is_buyout_team:
                            team_owes = int(full_buyout_cap * retained_pct)
                        # Bought out, someone else retained
                        elif is_buyout_team and retained.remaining_team != team:
                            team_owes = int(full_buyout_cap * (1 - retained_pct))
                        # Retained + Bought out (might be possible if OEL was traded back to UTA and then bought out maybe not)
                        else:
                            team_owes = full_buyout_cap
                    else:
                        team_owes = full_buyout_cap
                    buyout_seasons[season] = team_owes
                    season_totals[season] += team_owes
            if buyout_seasons:
                bought_out_contracts.append({
                    'player': contract.player, 'seasons': buyout_seasons, 'buyout_year': contract.buyout_year, 'is_retained': is_retaining_team and not is_buyout_team,
                    'retention_pct': retained.retention_percentage if retained and is_retaining_team else None,
                })

    buried_savings = 0

    for group in [forwards, defensemen, goalies]:
        for player_data in group:
            current_season_data = player_data['seasons'].get('2025-26')
            if current_season_data and current_season_data.get('roster_status') == 'buried':
                cap_hit_obj = current_season_data.get('cap_hit_obj')
                if cap_hit_obj:
                    retained = current_season_data.get('retained_amount', 0)
                    full_cap = cap_hit_obj.cap_hit - retained
                    buried_savings += full_cap - current_season_data['effective_cap_hit']
    
    def get_current_cap(player_data):
        current = player_data['seasons'].get('2025-26')
        if current:
            return current['effective_cap_hit']
        return 0

    
    forwards.sort(key=get_current_cap, reverse=True)
    defensemen.sort(key=get_current_cap, reverse=True)
    goalies.sort(key=get_current_cap, reverse=True)

    current_season = '2025-26'

    

    cap_ceiling = 95500000
    current_cap = season_totals[current_season]
    active_cap = current_cap - ltir_pool
    cap_space = cap_ceiling - current_cap + ltir_pool

    active_cap_pct = (active_cap / cap_ceiling) * 100 if cap_ceiling > 0 else 0
    ltir_pct = (ltir_pool / cap_ceiling) * 100 if cap_ceiling > 0 else 0
    space_pct = (cap_space / cap_ceiling) * 100 if cap_ceiling > 0 else 0

    context = {
        'team': team,
        'forwards': forwards,
        'defensemen': defensemen,
        'goalies': goalies,
        'display_seasons': display_seasons,
        'season_totals': season_totals,
        'cap_ceiling': cap_ceiling,
        'current_cap': current_cap,
        'active_cap': active_cap,
        'cap_space': cap_space,
        'ltir_pool': ltir_pool,
        'current_season': current_season,
        'retained_contracts': retained_contracts,
        'bought_out_contracts': bought_out_contracts,
        'buried_savings': buried_savings,
        'active_cap_pct': active_cap_pct,
        'ltir_pct': ltir_pct,
        'space_pct': space_pct,
    }

    return render(request, 'caps/team_overview.html', context)


def team_detail(request, abbreviation, season=None):
    team = get_object_or_404(Team, abbreviation=abbreviation.upper())
    players = team.players.all().order_by('last_name')
    
    available_seasons = [
        '2025-26', '2026-27', '2027-28', '2028-29', '2029-30', '2030-31', '2031-32', '2032-33',
    ]

    current_season = season if season in available_seasons else '2025-26'

    forwards = []
    defensemen = []
    goalies = []

    total_cap = 0
    ltir_pool = 0
    
    retained_contracts = []

    for retained in team.retained_contracts.all():
        contract = retained.contract
        if contract.status == 'active' and contract.player.current_team != team:

            cap_hit = contract.cap_hits.filter(season=current_season).first()
            if cap_hit:
                total_cap += retained.amount

                retained_contracts.append({
                    'player': contract.player, 'current_team': contract.player.current_team,
                    'retained_amount': retained.amount, 'retention_percentage': retained.retention_percentage,
                    'contract_end': contract.end_season
                })

    bought_out_contracts = []

    for contract in Contract.objects.filter(status='bought_out'):
        responsible_team = contract.buyout_team if contract.buyout_team else contract.signing_team


        # Oliver Ekman Larsson's Arizona/Utah contract was 12% retained, then traded to VAN and bought out. so they're on the hook for some
        # Pretty sure this is the only contract in the league like that
        retained = contract.retained_salaries.first()

        is_buyout_team = responsible_team == team
        is_retaining_team = (retained and retained.retaining_team ==team)

        if is_buyout_team or is_retaining_team:
                cap_hit_obj = contract.cap_hits.filter(season=season).first()
                if cap_hit_obj:
                    full_buyout_cap = cap_hit_obj.cap_hit

                    if retained:
                        retained_pct = float(retained.retention_percentage) / 100
                        # Only retained
                        if is_retaining_team and not is_buyout_team:
                            team_owes = int(full_buyout_cap * retained_pct)
                        # Bought out, someone else retained
                        elif is_buyout_team and retained.remaining_team != team:
                            team_owes = int(full_buyout_cap * (1 - retained_pct))
                        # Retained + Bought out (might be possible if OEL was traded back to UTA and then bought out maybe not)
                        else:
                            team_owes = full_buyout_cap
                    else:
                        team_owes = full_buyout_cap
                    total_cap += team_owes


                bought_out_contracts.append({
                    'player': contract.player, 'cap_hit': team_owes, 'buyout_year': contract.buyout_year, 'is_retained': is_retaining_team and not is_buyout_team,
                    'retention_pct': retained.retention_percentage if retained and is_retaining_team else None,
                })

    for player in players:
        contract_with_cap_hit = None
        cap_hit = None
        effective_cap_hit = 0
        retained_amount = 0

        for contract in player.contracts.filter(status__in=['active', 'future']):
            cap_hit = contract.cap_hits.filter(season=current_season).first()
            if cap_hit:
                contract_with_cap_hit = contract
                retained = contract.retained_salaries.first()
                if retained:
                    retained_amount = retained.amount
                else:
                    retained_amount = 0
                effective_cap_hit = calculate_effective_cap_hit(cap_hit, retained_amount, current_season)
                break

        if contract_with_cap_hit and cap_hit:
            player_data = {
                'player': player,
                'contract': contract_with_cap_hit,
                'cap_hit': cap_hit,
                'effective_cap_hit': effective_cap_hit,
                'retained_amount': retained_amount,
                }
            total_cap += effective_cap_hit

            if cap_hit.roster_status == 'ltir':
                ltir_pool += cap_hit.cap_hit - retained_amount


            if player.position in ['C', 'LW', 'RW']:
                forwards.append(player_data)
            elif player.position in ['LD', 'RD']:
                defensemen.append(player_data)
            elif player.position == 'G':
                goalies.append(player_data)
    
    
    # Sorts descending cap hits
    forwards.sort(key=lambda x: x['cap_hit'].cap_hit, reverse=True)
    defensemen.sort(key=lambda x: x['cap_hit'].cap_hit, reverse=True)
    goalies.sort(key=lambda x: x['cap_hit'].cap_hit, reverse=True)

    cap_ceiling = 95500000
    cap_space = cap_ceiling - total_cap + ltir_pool

    active_cap = total_cap - ltir_pool

    active_cap_pct = (active_cap / cap_ceiling) * 100 if cap_ceiling > 0 else 0
    ltir_pct = (ltir_pool / cap_ceiling) * 100 if cap_ceiling > 0 else 0
    space_pct = (cap_space / cap_ceiling) * 100 if cap_ceiling > 0 else 0
    
    context = {
        'team': team,
        'forwards': forwards,
        'defensemen': defensemen,
        'goalies': goalies,
        'total_cap': total_cap,
        'cap_ceiling': cap_ceiling,
        'cap_space': cap_space,
        'current_season': current_season,
        'available_seasons': available_seasons,
        'ltir_pool': ltir_pool,
        'retained_contracts': retained_contracts,
        'bought_out_contracts': bought_out_contracts,
        'active_cap_pct': active_cap_pct,
        'ltir_pct': ltir_pct,
        'space_pct': space_pct,
        'active_cap': active_cap,
        
    }

    return render(request, 'caps/team_detail.html', context)