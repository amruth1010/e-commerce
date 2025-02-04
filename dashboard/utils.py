def calculate_growth_percentage(current_value, previous_value):
    if previous_value == 0:
        return 0
    return ((current_value - previous_value) / previous_value) * 100