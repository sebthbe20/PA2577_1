from datetime import datetime, timezone

day = 60*60*24 * 1000
week = 60*60*24*7 * 1000
year = 60*60*24*365 * 1000

def calculate_expiry(time: str):

    if time == "never":
        return None

    cur_time = int(datetime.now(timezone.utc).timestamp() * 1000)

    if time[-1] == "d":
        expiry = cur_time + int(time[:-1])*day

    elif time[-1] == "w":
        expiry = cur_time + int(time[:-1])*week

    elif time[-1] == "y":
        expiry = cur_time + int(time[:-1])*year

    else:
        raise ValueError(f"Invalid input for expiry")

    return expiry

