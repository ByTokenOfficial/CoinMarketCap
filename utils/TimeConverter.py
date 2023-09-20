from datetime import datetime
import pytz


def convert_timezone(t):
    target_timezone = pytz.timezone("Asia/Taipei")
    target_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC).astimezone(target_timezone)
    formatted_target_time = target_time.strftime("%Y-%m-%d %H:%M:%S%z")
    return formatted_target_time

if __name__ == '__main__':
    pass