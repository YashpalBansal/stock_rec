from datetime import datetime

PUNJABI_SEASONS = [
    (3, 4, "Spring", "Chet"), (4, 5, "Summer", "Vaisakh"),
    (5, 6, "Peak Summer", "Jeth"), (6, 7, "Pre-Monsoon", "Harr"),
    (7, 9, "Rainy", "Saun/Bhado"), (9, 10, "Autumn", "Assu"),
    (10, 11, "Festive", "Katak"), (11, 12, "Winter", "Maghar"),
    (12, 1, "Peak Winter", "Poh"), (1, 2, "Winter", "Magh"),
    (2, 3, "Spring", "Phagun")
]

def get_punjabi_season(date_obj):
    m = date_obj.month
    for start_m, end_m, season, _ in PUNJABI_SEASONS:
        if start_m < end_m:
            if start_m <= m <= end_m: return season
        else:
            if m >= start_m or m <= end_m: return season
    return "Unknown"

def calculate_weighted_avg_price(conn, item_id):
    result = conn.execute(
        'SELECT SUM(total_cost) as total_cost, SUM(quantity_bought) as total_qty FROM Purchase WHERE item_id = ?',
        (item_id,)
    ).fetchone()
    if result and result['total_qty'] and result['total_qty'] > 0:
        return result['total_cost'] / result['total_qty']
    return 0

def check_demand_spike(conn, item_id, current_daily_usage):
    stats = conn.execute('SELECT daily_usage FROM Item_Stats WHERE item_id = ?', (item_id,)).fetchone()
    if stats and stats['daily_usage'] > 0:
        if current_daily_usage > 1.5 * stats['daily_usage']:
            return True
    return False

def update_season_stats(conn, item_id, purchase_date_str, consumption):
    if consumption <= 0: return
    date_obj = datetime.strptime(purchase_date_str, '%Y-%m-%d')
    season = get_punjabi_season(date_obj)
    year = date_obj.year

    stat = conn.execute('SELECT id, total_consumption FROM Season_Stats WHERE item_id = ? AND season_name = ? AND year = ?',
                        (item_id, season, year)).fetchone()
    if stat:
        new_consumption = stat['total_consumption'] + consumption
        conn.execute('UPDATE Season_Stats SET total_consumption = ? WHERE id = ?', (new_consumption, stat['id']))
    else:
        conn.execute('INSERT INTO Season_Stats (item_id, season_name, year, total_consumption, season_index) VALUES (?, ?, ?, ?, ?)',
                     (item_id, season, year, consumption, 1.0))
