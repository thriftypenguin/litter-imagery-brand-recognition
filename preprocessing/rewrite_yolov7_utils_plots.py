from run import replace_line

file_name = 'yolov7/utils/plots.py'

line_number_to_replace = 21
new_line = 'from yolov7.utils.general import xywh2xyxy, xyxy2xywh'
replace_line(file_name, line_number_to_replace, new_line)

line_number_to_replace = 22
new_line = 'from yolov7.utils.metrics import fitness'
replace_line(file_name, line_number_to_replace, new_line)