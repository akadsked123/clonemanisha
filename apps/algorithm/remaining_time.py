from datetime import timedelta
def format_remaining_time(remaining_time):
      td = timedelta(seconds=remaining_time)
      days = td.days
      hours, remainder = divmod(td.seconds, 3600)
      minutes, seconds = divmod(remainder, 60)
      time_str = ""
      if days > 0:
          time_str += f"{days} day{'s' if days > 1 else ''}"
      if hours > 0:
          if time_str:
              time_str += " and "
          time_str += f"{hours} hour{'s' if hours > 1 else ''}"
      if minutes > 0:
          if time_str:
              time_str += " and "
          time_str += f"{minutes} minute{'s' if minutes > 1 else ''}"
      if seconds > 0 and not time_str:
          time_str += f"{seconds} second{'s' if seconds > 1 else ''}"
      return time_str