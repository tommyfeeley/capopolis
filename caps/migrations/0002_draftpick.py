import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caps', '0001_add_draftpick'),
    ]

    operations = [
        migrations.CreateModel(
            name='DraftPick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('round', models.PositiveSmallIntegerField(choices=[(1, 'Round 1'), (2, 'Round 2'), (3, 'Round 3'), (4, 'Round 4'), (5, 'Round 5'), (6, 'Round 6'), (7, 'Round 7')])),
                ('is_conditional', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, help_text='Condition details, trade notes, etc.')),
                ('current_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_picks', to='caps.team')),
                ('original_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='original_picks', to='caps.team')),
            ],
            options={
                'ordering': ['year', 'round'],
                'unique_together': {('year', 'round', 'original_team')},
            },
        ),
    ]
