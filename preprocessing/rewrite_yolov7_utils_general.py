from run import replace_line

file_name = 'yolov7/utils/general.py'

line_number_to_replace = 21
new_line = 'from yolov7.utils.google_utils import gsutil_getsize'
replace_line(file_name, line_number_to_replace, new_line)

line_number_to_replace = 22
new_line = 'from yolov7.utils.metrics import fitness'
replace_line(file_name, line_number_to_replace, new_line)

line_number_to_replace = 23
new_line = 'from yolov7.utils.torch_utils import init_torch_seeds'
replace_line(file_name, line_number_to_replace, new_line)