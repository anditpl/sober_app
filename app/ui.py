"""
Module: ui
Handles the console-based user interface, including calendar display.
"""

import calendar
from datetime import datetime
from colorama import Fore, Back, Style
from .data_manager import load_data

def display_calendar(year: int, month: int, data: dict) -> None:
    """
    Displays a formatted calendar for the specified month.
    Days with log entries are color-coded:
      - Green for sober days.
      - Red for drinking days.
    Also prints monthly statistics if available.
    """
    cal = calendar.monthcalendar(year, month)
    calendar.setfirstweekday(calendar.MONDAY)
    
    week_header = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    header_str = " ".join(f"{day:>3}" for day in week_header)
    print(Fore.CYAN + f"\nCalendar for {month}/{year}")
    print(Fore.WHITE + header_str)
    
    daily_log = load_data().get("daily_log", {})
    
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "    "
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in daily_log:
                    record = daily_log[date_str]
                    if record.get("sober", False):
                        week_str += Back.GREEN + f"{day:3d}" + Style.RESET_ALL + " "
                    else:
                        week_str += Back.RED + f"{day:3d}" + Style.RESET_ALL + " "
                else:
                    week_str += f"{day:3d} "
        print(week_str)
    
    total = 0
    sober = 0
    spent = 0.0
    for date_str, record in daily_log.items():
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            continue
        if d.year == year and d.month == month:
            total += 1
            if record.get("sober", False):
                sober += 1
            else:
                try:
                    amt = float(record.get("amount_spent", 40))
                except Exception:
                    amt = 40.0
                if amt == 0:
                    amt = 40.0
                spent += amt
    if total > 0:
        percent = sober / total * 100
        print(Fore.CYAN + f"\nStatistics for {month}/{year}:")
        print(Fore.YELLOW + f"{sober} sober days out of {total} days ({percent:.2f}%), spent: {spent:.2f} $")
    else:
        print(Fore.YELLOW + "\nNo data available for the selected month.")

def display_current_calendar() -> None:
    """
    Displays the calendar for the current month.
    """
    data = load_data()
    now = datetime.now()
    display_calendar(now.year, now.month, data)

def display_given_calendar() -> None:
    """
    Prompts the user for a year and month, then displays the corresponding calendar and statistics.
    """
    data = load_data()
    try:
        year = int(input(Fore.CYAN + "Enter year (e.g., 2025): ").strip())
        month = int(input(Fore.CYAN + "Enter month (1-12): ").strip())
        if not (1 <= month <= 12):
            raise ValueError
    except Exception:
        print(Fore.RED + "Invalid year or month.")
        return
    display_calendar(year, month, data)
