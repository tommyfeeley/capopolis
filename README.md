![Capopolis](https://github.com/user-attachments/assets/3a66e491-99ae-44bf-a101-4840228c9d85)
# Capopolis
(screenshots/Capopolis.png)

An NHL salary cap tracking application built with Django that models the full complexity of the NHL's Collective Bargaining Agreement — including buried contracts, LTIR relief, buyout calculations, retained salary, and performance bonus overages.

Covers all 32 NHL teams with 898 players, 970 contracts, and 3,677 individual season cap hits manually entered for accuracy.

![Team Overview](screenshots/team_overview.png)

## Features

### Multi-Season Cap Overview
Each team page shows a full roster breakdown across 6 seasons, sorted by position group (forwards, defensemen, goalies). Cap hits are color-coded by roster status — active, LTIR, IR, and buried contracts each have distinct colors so you can scan a roster at a glance.

A visual cap bar shows the breakdown between active cap, LTIR pool, and available cap space.

![Cap Bar](screenshots/cap_bar.png)

### Season Detail View
Drill into any single season for a detailed breakdown including base salary, signing bonuses, roster status badges, contract clauses (NMC, NTC, M-NTC with team counts), and expiration info.

![Season Detail](screenshots/season_detail.png)

### Trade Simulator / Cap Calculator
Toggle into Cap Calculator mode on any team page to simulate trades in real time:

- **Remove players** — uncheck any player to see how moving them off the roster affects the team's cap. LTIR relief recalculates automatically.
- **Add players from other teams** — instant trie-based search across all 857 players in the database. Results appear as you type with no API calls or loading — the entire player index is built into a client-side trie on page load.
- **Retained salary** — when adding a player, set any retained salary percentage from 0–50% with preset buttons (0%, 25%, 50%) or a precise slider/input for specific values like 16.67%.
- **Custom players** — create hypothetical players with custom cap hits and positions for "what if" scenarios.
- **Live tracking panel** — a floating panel shows all changes, net cap impact, and updated cap space. Season totals update for the current season as you make changes.

![Cap Calculator](screenshots/cap_calculator.png)

### Buyout Calculator
Click "Buyout" on any player to see a full breakdown of what their buyout would cost:

- Calculates based on age (over/under 26 threshold), remaining salary, and contract length
- Spreads the buyout cost over 2x the remaining years
- Accounts for signing bonuses that are still owed during originally scheduled seasons
- Shows per-season cap hit and cash cost

![Buyout Modal](screenshots/buyout_modal.png)

### CBA Rules Modeled
- **Buried contracts** — players sent to the AHL only count against the cap above the buried contract threshold ($1.15M), saving teams significant cap space on depth contracts
- **LTIR relief** — Long-Term Injured Reserve players' cap hits create additional cap space for the team, tracked separately from standard cap space
- **Retained salary** — when a player is traded, the original team can retain a percentage (up to 50%) of the cap hit, which counts against *their* cap ceiling
- **Buyout penalties** — bought-out contracts create dead cap charges spread over double the remaining contract years
- **Performance bonus overages** — entry-level contract bonuses that push a team over the cap carry over as penalties the following season

### Retained Salary on Bought-Out Contracts
The system correctly handles edge cases like Oliver Ekman-Larsson's contract, where salary was retained by one team, the player was traded, and then bought out by the acquiring team — splitting the buyout dead cap between the retaining team and the buying-out team.

## Tech Stack

- **Backend:** Python / Django
- **Database:** SQLite
- **Frontend:** Django templates, vanilla JavaScript
- **Search:** Client-side trie data structure for instant player lookup (indexed by first name, last name, and full name)

## Data

All contract data was manually entered through the Django admin interface. The database includes:

| | Count |
|---|---|
| Teams | 32 |
| Players | 857 |
| Contracts | 921 |
| Season Cap Hits | 3,543 |

## Project Structure

```
caps/
├── models.py          # Team, Player, Contract, CapHit, RetainedSalary, CapPenalty
├── views.py           # Team overview, season detail, player search API
├── urls.py            # URL routing
├── admin.py           # Django admin with inline cap hit editing
├── templatetags/
│   └── cap_filters.py # Custom template filters (dict lookup, JSON serialization)
└── templates/caps/
    ├── home.html           # Homepage with all 32 teams by division
    ├── team_overview.html  # Multi-season roster + cap calculator
    └── team_detail.html    # Single-season detail view
```

## Setup

```bash
# Clone the repo
git clone https://github.com/tommyfeeley/capopolis.git
cd capopolis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install django

# Run migrations
python manage.py migrate

# Create a superuser (for admin access to add/edit data)
python manage.py createsuperuser

# Run the dev server
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` to see the app, or `http://127.0.0.1:8000/admin/` to manage data.

## Screenshots

> **Note:** Replace the placeholder image paths above with actual screenshots. See the recommended screenshots section below.

### Recommended Screenshots

1. **`screenshots/team_overview.png`** — Full team overview page showing the roster tables, cap summary boxes, and cap bar. Pick a team with interesting cap situations (NJD has LTIR players and buried contracts).

2. **`screenshots/cap_bar.png`** — Close-up of the cap summary boxes and the colored cap breakdown bar. Crop just the top section of the team overview page.

3. **`screenshots/season_detail.png`** — The single-season detail view showing salary breakdowns, status badges, and trade clause indicators (NMC, NTC, M-NTC).

4. **`screenshots/cap_calculator.png`** — Cap calculator mode active with a couple players unchecked and one player added from another team via the search. Show the floating tracker panel with the net cap change.

5. **`screenshots/buyout_modal.png`** — The buyout calculator modal open for a player, showing the per-season breakdown table.

## License

This project is for educational and portfolio purposes. NHL team names, player names, and contract data are property of the NHL and NHLPA.
