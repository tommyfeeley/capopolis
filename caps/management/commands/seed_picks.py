from django.core.management.base import BaseCommand
from caps.models import Team, DraftPick


class Command(BaseCommand):
    help = 'Seed draft picks so every team owns their own pick for rounds 1-7 across a range of years.'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=int, default=2024, help='First draft year (default: 2024)')
        parser.add_argument('--end', type=int, default=2031, help='Last draft year inclusive (default: 2031)')
        parser.add_argument('--overwrite', action='store_true', help='Skip existing picks instead of failing')

    def handle(self, *args, **options):
        teams = list(Team.objects.all())
        if not teams:
            self.stderr.write('No teams found. Add teams first.')
            return

        start, end = options['start'], options['end']
        created = skipped = 0

        for year in range(start, end + 1):
            for round_num in range(1, 8):
                for team in teams:
                    pick, was_created = DraftPick.objects.get_or_create(
                        year=year,
                        round=round_num,
                        original_team=team,
                        defaults={'current_team': team},
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created} picks, skipped {skipped} existing.'
        ))
