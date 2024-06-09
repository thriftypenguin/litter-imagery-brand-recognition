from run import replace_line

file_name = '/usr/local/lib/python3.10/dist-packages/yolov7_package/models/experimental.py'

line_number_to_replace = 7
new_line = 'from yolov7_package.utils.google_utils import attempt_download'
replace_line(file_name, line_number_to_replace, new_line)

line_number_to_replace = 241
new_line = '        w = "Logo_detection_YoloV7/"+w+"/"'
replace_line(file_name, line_number_to_replace, new_line)

line_number_to_replace = 242
new_line = '        ckpt = torch.load("Logo_detection_YoloV7/logo_detection.pt")'
replace_line(file_name, line_number_to_replace, new_line)

