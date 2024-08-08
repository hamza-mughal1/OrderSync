def percentage_difference(value1, value2):
    """
    Calculate how much percentage value1 is less or more than value2.
    
    Args:
    value1 (float): The first value.
    value2 (float): The second value.
    
    Returns:
    float: The percentage difference.
    str: A description indicating whether value1 is more or less than value2.
    """
    if value2 == 0:
        raise ValueError("The second value (value2) cannot be zero.")
    
    # Determine which value is larger
    larger_value = max(value1, value2)
    smaller_value = min(value1, value2)
    
    difference = larger_value - smaller_value
    percentage_diff = (difference / smaller_value) * 100
    
    if value1 > value2:
        return percentage_diff, f"{value1} is {percentage_diff:.2f}% more than {value2}."
    elif value1 < value2:
        return percentage_diff, f"{value1} is {percentage_diff:.2f}% less than {value2}."
    else:
        return 0, f"{value1} is equal to {value2}."

# Example usage:
value1 = int(input("enter the value: "))
value2 = int(input("enter the value: "))
percentage_diff, description = percentage_difference(value1, value2)
print(f"Percentage Difference: {percentage_diff:.2f}%")
print(description)
