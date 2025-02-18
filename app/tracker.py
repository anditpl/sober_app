"""
Module: tracker
Contains the SobrietyTracker class for managing log entries and computing statistics.
"""

from datetime import datetime, timedelta
from .data_manager import load_data, save_data
from .constants import DEFAULT_AMOUNT, MONTH_NAMES

class SobrietyTracker:
    """
    A class to manage sobriety logs and compute statistics.
    """
    def __init__(self):
        self.data = load_data()

    def log_entry(self, date_str: str, sober: bool, mood: str, notes: str,
                  alcohol_type: str = "", alcohol_amount: str = "", amount_spent: float = 0.0) -> None:
        """
        Logs an entry for a given date.

        Parameters:
            date_str (str): Date in 'YYYY-MM-DD' format. If empty, today's date is used.
            sober (bool): True if sober, False if alcohol was consumed.
            mood (str): Mood description.
            notes (str): Additional notes or triggers.
            alcohol_type (str): Type of alcohol (if consumed).
            alcohol_amount (str): Amount consumed.
            amount_spent (float): Amount spent on alcohol.
        """
        try:
            if not date_str:
                date_obj = datetime.now()
                date_str = date_obj.strftime("%Y-%m-%d")
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            print(f"Error in date format: {e}")
            return

        self.data["daily_log"][date_str] = {
            "sober": sober,
            "mood": mood,
            "notes": notes,
            "alcohol_type": alcohol_type,
            "alcohol_amount": alcohol_amount,
            "amount_spent": amount_spent
        }
        try:
            save_data(self.data)
        except Exception as e:
            print(f"Error saving log entry: {e}")

    def get_all_entries(self) -> dict:
        """
        Returns all log entries.
        """
        return self.data.get("daily_log", {})

    def get_statistics(self) -> dict:
        """
        Computes and returns monthly and yearly statistics.

        Returns:
            dict: Contains keys 'monthly' and 'yearly' with computed stats.
        """
        stats = {"monthly": {}, "yearly": {}}
        daily_log = self.get_all_entries()
        for date_str, record in daily_log.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                continue
            month_key = date_obj.strftime("%Y-%m")
            if month_key not in stats["monthly"]:
                stats["monthly"][month_key] = {"sober_days": 0, "total_days": 0, "spent": 0.0}
            stats["monthly"][month_key]["total_days"] += 1
            if record.get("sober", False):
                stats["monthly"][month_key]["sober_days"] += 1
            else:
                try:
                    amt = float(record.get("amount_spent", DEFAULT_AMOUNT))
                except Exception:
                    amt = DEFAULT_AMOUNT
                if amt == 0:
                    amt = DEFAULT_AMOUNT
                stats["monthly"][month_key]["spent"] += amt

            year_key = date_obj.strftime("%Y")
            if year_key not in stats["yearly"]:
                stats["yearly"][year_key] = {"sober_days": 0, "total_days": 0}
            stats["yearly"][year_key]["total_days"] += 1
            if record.get("sober", False):
                stats["yearly"][year_key]["sober_days"] += 1
        return stats

    def get_additional_stats(self) -> dict:
        """
        Computes additional statistics such as total days, percentage sober,
        longest sober streak, and current sober streak.

        Returns:
            dict: Contains 'total_days', 'percent_sober', 'longest_streak', and 'current_streak'.
        """
        daily_log = self.get_all_entries()
        sorted_dates = sorted(daily_log.keys())
        total_days = len(sorted_dates)
        sober_days = sum(1 for d in daily_log if daily_log[d].get("sober", False))
        percent_sober = (sober_days / total_days * 100) if total_days else 0

        longest_streak = 0
        current_streak = 0
        previous_date = None
        for date_str in sorted_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                continue
            if daily_log[date_str].get("sober", False):
                if previous_date and (date_obj - previous_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0
            previous_date = date_obj

        # Calculate current streak from latest entry backwards
        current_seq = 0
        for date_str in reversed(sorted_dates):
            if daily_log[date_str].get("sober", False):
                current_seq += 1
            else:
                break

        return {
            "total_days": total_days,
            "percent_sober": percent_sober,
            "longest_streak": longest_streak,
            "current_streak": current_seq
        }

    def print_statistics(self) -> None:
        """
        Prints monthly, yearly, additional statistics, and spending information in a formatted manner.
        """
        stats = self.get_statistics()
        add_stats = self.get_additional_stats()
        print("\n=== Monthly Statistics (Log) ===")
        for month_key in sorted(stats["monthly"].keys()):
            m_stat = stats["monthly"][month_key]
            # Format month using the MONTH_NAMES constant
            try:
                year, month = month_key.split("-")
                month_name = MONTH_NAMES.get(month, month)
                formatted_month = f"{month_name} {year}"
            except Exception:
                formatted_month = month_key
            percent = (m_stat["sober_days"] / m_stat["total_days"] * 100) if m_stat["total_days"] else 0
            print(f"{formatted_month}: {m_stat['sober_days']} sober days out of {m_stat['total_days']} days ({percent:.2f}%), spent: {m_stat['spent']:.2f} $")

        print("\n=== Yearly Statistics (Log) ===")
        for year_key in sorted(stats["yearly"].keys()):
            y_stat = stats["yearly"][year_key]
            percent = (y_stat["sober_days"] / y_stat["total_days"] * 100) if y_stat["total_days"] else 0
            print(f"{year_key}: {y_stat['sober_days']} sober days out of {y_stat['total_days']} days ({percent:.2f}%)")

        print("\n=== Additional Statistics (Log) ===")
        print(f"Total days in log: {add_stats['total_days']}")
        print(f"Percentage sober: {add_stats['percent_sober']:.2f}%")
        print(f"Longest sober streak: {add_stats['longest_streak']} days")
        print(f"Current sober streak: {add_stats['current_streak']} days")

        # Calculate spending details
        overall_spending = 0.0
        current_month_spending = 0.0
        now = datetime.now()
        for date_str, record in self.get_all_entries().items():
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
        print("\n=== Alcohol Spending (Log) ===")
        print(f"Total amount spent on alcohol (overall): {overall_spending:.2f} $")
        print(f"Total amount spent on alcohol (current month): {current_month_spending:.2f} $")
