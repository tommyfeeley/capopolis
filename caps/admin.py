from django.contrib import admin
from .models import Team, Player, Contract, CapHit, RetainedSalary
# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['city', 'name', 'abbreviation', 'conference', 'division']
    list_filter = ['conference', 'division']
    search_fields = ['name', 'city', 'abbreviation']
    ordering = ['name']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position', 'current_team']
    list_filter = ['position', 'current_team']
    search_fields = ['first_name', 'last_name']
    ordering = ['last_name', 'first_name']

class CapHitInLine(admin.TabularInline):
    model = CapHit
    extra = 1
    ordering = ['season']

class RetainedSalaryInLine(admin.TabularInline):
    model = RetainedSalary
    extra = 0

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['player', 'signing_team', 'aav', 'start_season', 'end_season', 'status']
    list_filter = ['status', 'signing_team', 'is_two_way', 'is_entry_level']
    search_fields = ['player__first_name', 'player__last_name']
    ordering = ['-aav']
    inlines = [CapHitInLine, RetainedSalaryInLine]

    fieldsets = (
        ('Player & Team', {
            'fields': ('player', 'signing_team', 'status')
        }),
        ('Contract Terms',
         {
             'fields': ('total_years', 'total_value', 'aav', 'signing_date', 'start_season', 'end_season')

         }),
         ('Contract Type',
          {
              'fields': ('is_two_way', 'is_entry_level', 'notes')
          }),

    )

@admin.register(CapHit)
class CapHitAdmin(admin.ModelAdmin):
    list_display = ['contract', 'season', 'cap_hit', 'nhl_salary', 'roster_status']
    list_filter = ['season', 'roster_status']
    search_fields = ['contract__player__first_name', 'contract__player__last_name']
    ordering = ['season']

@admin.register(RetainedSalary)
class RetainedSalaryAdmin(admin.ModelAdmin):
    list_display = ['contract', 'retaining_team', 'amount', 'retention_percentage']
    list_filter = ['retaining_team']
    search_fields = ['contract__player__first_name', 'contract__player__last_name']
