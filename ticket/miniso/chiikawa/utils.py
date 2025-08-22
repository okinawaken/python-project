from datetime import datetime


def time_str_to_timestamp(time_str, original_format):
    dt = datetime.strptime(time_str, original_format)
    return dt.timestamp()


def time_str_format(time_str, original_format, target_format):
    dt = datetime.strptime(time_str, original_format)
    return dt.strftime(target_format)
