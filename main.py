"""
Main entry point for the Sobriety Tracking Application.
"""

from app.data_manager import load_data
from app.tracker import SobrietyTracker
from app.ui import display_current_calendar, display_given_calendar
from app.report import ExcelReport
from app.constants import MONTH_NAMES, DEFAULT_AMOUNT
from colorama import Fore
from datetime import datetime

def main_menu() -> None:
    """
    Main menu loop.
    """
    data = load_data()
    tracker = SobrietyTracker()
    
    # Display current month's calendar on startup
    display_current_calendar()
    
    while True:
        print(Fore.CYAN + "\n--- Sobriety Tracking Application ---")
        print(Fore.YELLOW + "1. Add log entry")
        print(Fore.YELLOW + "2. Show all statistics")
        print(Fore.YELLOW + "3. Export report to Excel")
        print(Fore.YELLOW + "4. Display calendar for a given month")
        print(Fore.YELLOW + "5. Exit")
        choice = input(Fore.CYAN + "Select an option: ").strip()

        if choice == "1":
            # Prompt user for log entry details (if sober, skip alcohol-related prompts)
            date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()
            status_input = input("Consumed alcohol? (y/n): ").strip().lower()
            sober = (status_input == "n")
            mood = input("Enter mood: ")
            notes = input("Enter notes: ")
            if not sober:
                alcohol_type = input("Enter type of alcohol: ")
                alcohol_amount = input("Enter amount consumed: ")
                try:
                    amount_spent = float(input("Enter amount spent: ") or 0)
                except Exception:
                    amount_spent = 0.0
            else:
                alcohol_type = ""
                alcohol_amount = ""
                amount_spent = 0.0
            tracker.log_entry(date_str, sober, mood, notes, alcohol_type, alcohol_amount, amount_spent)
        elif choice == "2":
            print(Fore.BLUE + "\n========= ALL STATISTICS =========")
            stats = tracker.get_statistics()
            
            # Monthly Statistics in GREEN
            print(Fore.GREEN + "\n=== Monthly Statistics (Log) ===")
            for month_key in sorted(stats["monthly"].keys()):
                m_stat = stats["monthly"][month_key]
                try:
                    year_str, month_str = month_key.split("-")
                    month_name = MONTH_NAMES.get(month_str, month_str)
                    formatted_month = f"{month_name} {year_str}"
                except Exception:
                    formatted_month = month_key
                percent = (m_stat["sober_days"] / m_stat["total_days"] * 100) if m_stat["total_days"] else 0
                print(Fore.GREEN + f"{formatted_month}: {m_stat['sober_days']} sober days out of {m_stat['total_days']} days ({percent:.2f}%), spent: {m_stat['spent']:.2f} $")
            
            # Yearly Statistics in CYAN
            print(Fore.CYAN + "\n=== Yearly Statistics (Log) ===")
            for year_key in sorted(stats["yearly"].keys()):
                y_stat = stats["yearly"][year_key]
                percent = (y_stat["sober_days"] / y_stat["total_days"] * 100) if y_stat["total_days"] else 0
                print(Fore.CYAN + f"{year_key}: {y_stat['sober_days']} sober days out of {y_stat['total_days']} days ({percent:.2f}%)")
            
            # Additional Statistics in MAGENTA
            add_stats = tracker.get_additional_stats()
            print(Fore.MAGENTA + "\n=== Additional Statistics (Log) ===")
            print(Fore.MAGENTA + f"Total days in log: {add_stats['total_days']}")
            print(Fore.MAGENTA + f"Percentage sober: {add_stats['percent_sober']:.2f}%")
            print(Fore.MAGENTA + f"Longest sober streak: {add_stats['longest_streak']} days")
            print(Fore.MAGENTA + f"Current sober streak: {add_stats['current_streak']} days")
            
            # Alcohol Spending in YELLOW
            overall_spending = 0.0
            current_month_spending = 0.0
            now = datetime.now()
            daily_log = tracker.get_all_entries()
            for date_str, record in daily_log.items():
                try:
                    d = datetime.strptime(date_str, "%Y-%m-%d")
                except Exception:
                    continue
                if not record.get("sober", False):
                    try:
                        amt = float(record.get("amount_spent", DEFAULT_AMOUNT))
                        if amt == 0:
                            amt = DEFAULT_AMOUNT
                    except Exception:
                        amt = DEFAULT_AMOUNT
                    overall_spending += amt
                    if d.year == now.year and d.month == now.month:
                        current_month_spending += amt
            print(Fore.YELLOW + "\n=== Alcohol Spending (Log) ===")
            print(Fore.YELLOW + f"Total amount spent on alcohol (overall): {overall_spending:.2f} $")
            print(Fore.YELLOW + f"Total amount spent on alcohol (current month): {current_month_spending:.2f} $")
            print(Fore.BLUE + "==================================\n")
        elif choice == "3":
            report = ExcelReport(data)
            now = datetime.now()
            month_name = MONTH_NAMES.get(now.strftime("%m"), now.strftime("%m"))
            filename = f"report {month_name} {now.year}.xlsx"
            report.generate(filename)
        elif choice == "4":
            display_given_calendar()
        elif choice == "5":
            print(Fore.GREEN + "Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
