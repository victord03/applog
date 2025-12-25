
def format_date(iso_date_str) -> str:
    """Format ISO date string to DD/MM/YYYY. Works with both strings and Reflex Vars."""
    try:
        from datetime import datetime
        # Convert to string immediately - no conditionals on Var parameter
        str_date = str(iso_date_str)
        # Now check the string value
        if str_date in ("", "None", "null"):
            return ""
        dt = datetime.fromisoformat(str_date)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError, TypeError):
        return ""