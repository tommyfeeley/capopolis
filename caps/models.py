from django.db import models

# Create your models here.

class Team(models.Model):
    CONFERENCE_CHOICES = [ ('east', 'Eastern'), ('west', 'Western'),]

    DIVISION_CHOICES = [('atlantic', 'Atlantic'), ('metropolitan', 'Metropolitan'), ('central', 'Central'), ('pacific', 'Pacific'),]

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    abbreviation = models.CharField(max_length=3)
    conference = models.CharField(max_length=20, choices=CONFERENCE_CHOICES)
    division = models.CharField(max_length=20, choices=DIVISION_CHOICES)

    def __str__(self):
        return f"{self.city} {self.name}"
    
class Player(models.Model):
    POSITION_CHOICES = [('C', 'Center'), ('LW', 'Left Wing'), ('RW', 'Right Wing'), ('LD', 'Left Defense'), ('RD', 'Right Defense'), ('G', 'Goalie'),]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    secondary_position = models.CharField(max_length=2, choices=POSITION_CHOICES, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    current_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_positions_displayed(self):
        if self.secondary_position:
            return f"{self.position}/{self.secondary_position}"
        return self.position
    
class Contract(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('bought_out', 'Bought Out'), ('terminated', 'Terminated'), ('expired', 'Expired'), ('future', 'Future',)]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='contracts')

    signing_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='signed_contracts')

    total_years = models.PositiveIntegerField()
    total_value = models.PositiveIntegerField()
    aav = models.PositiveIntegerField()
    signing_date = models.DateField(null=True, blank=True)
    start_season = models.CharField(max_length=7)
    end_season = models.CharField(max_length=7)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')

    is_two_way = models.BooleanField(default=False)
    is_entry_level = models.BooleanField(default=False)

    notes = models.TextField(blank=True)


    def __str__(self):
        return f"{self.player} - {self.aav:,}/yr ({self.start_season} to {self.end_season})"
    
class CapHit(models.Model):
    ROSTER_STATUS_CHOICES = [('active', 'Active'), ('buried', 'Buried'), ('ir', 'Injured Reserve'), ('ltir', 'Long-Term IR'),]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='cap_hits')

    season = models.CharField(max_length=7)


    cap_hit = models.PositiveIntegerField()
    nhl_salary = models.PositiveIntegerField()
    ahl_salary = models.PositiveIntegerField(null=True, blank=True)
    signing_bonus = models.PositiveIntegerField(default=0)

    roster_status = models.CharField(max_length=10, choices=ROSTER_STATUS_CHOICES, default='active')

    has_nmc = models.BooleanField(default=False)
    has_ntc = models.BooleanField(default=False)
    has_modified_ntc = models.BooleanField(default=False)
    ntc_teams_can_block = models.PositiveIntegerField(null=True, blank=True)

    performance_bonus_potential = models.PositiveIntegerField(default=0)
    performance_bonus_earned = models.PositiveIntegerField(default=0)
    

    class Meta:
        verbose_name_plural = "Cap Hits"
        unique_together = ['contract', 'season']
    
    def __str__(self):
        return f"{self.contract.player} - {self.season}: ${self.cap_hit:,}"
    
class RetainedSalary(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='retained_salaries')
    retaining_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='retained_contracts')
    amount = models.PositiveIntegerField()
    retention_percentage = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        verbose_name_plural = "Retained Salaries"

    def __str__(self):
        return f"{self.retaining_team.abbreviation} retaining ${self.amount:} on {self.contract.player}"
    