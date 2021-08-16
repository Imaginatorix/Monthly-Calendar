from dataclasses import dataclass, field
from PIL import ImageFont
import Find
import time

@dataclass
class Calendar_Settings():
    title: str = ""
    year: int = int(time.strftime('%Y', time.localtime(time.time())))
    month: int = int(time.strftime('%m', time.localtime(time.time())))
    day_start: int = 6 # 0 = Monday... 6 = Sunday
    day_name_length: int = 3
    show_month: bool = True
    show_year: bool = False
    legend: bool = True
    message_of_the_month: bool = False
    message_title: str = None
    message_subtitle: str = None
    allowed_events: tuple = tuple(Find.all_events())

@dataclass
class Calendar_Month_Style():
    # font heights here is maximimzed, so that when it is used, there is already padding
    tallest_word: str = "Wy"

    image_bg: tuple = (255, 255, 255, 255)

    day_font_size: int = 60
    day_font: ImageFont = Find.image_font(day_font_size, True)
    day_height: int = int(day_font.getsize(tallest_word)[1] * (1.5))
    day_width: int = int(day_height * (1.5))
    day_color_weekday: tuple = (0, 0, 0, 255)
    day_color_weekend: tuple = (61, 109, 194, 255)
    pad_x: int = 85
    pad_y: int = 30

    line_x_color: tuple = (128, 100, 162, 255)
    line_x_width: int = 5
    line_y_color: tuple = (128, 100, 162, 255)
    line_y_width: int = 5
    
    title_font: ImageFont = Find.image_font(68, True)
    title_height: int = title_font.getsize(tallest_word)[1]
    title_color: tuple = (0, 0, 0, 255)
    title_padding: int = 30

    month_title_font: ImageFont = Find.image_font(100, True)
    month_title_height: int = month_title_font.getsize(tallest_word)[1]
    month_title_color: tuple = (0, 0, 0, 255)

    day_title_box_color: tuple = (128, 100, 162, 255)
    day_title_box_padding: int = 45

    day_title_font: ImageFont = Find.image_font(60, True)
    day_title_height: int = day_title_font.getsize(tallest_word)[1]
    day_title_color_weekday: tuple = (255, 255, 255, 255)
    day_title_color_weekend: tuple = (189, 209, 255, 255)

    legend_title_show: bool = True
    legend_title_font: ImageFont = Find.image_font(48, True)
    legend_title_height: int = legend_title_font.getsize(tallest_word)[1]
    legend_title_color: tuple = (0, 0, 0, 255)

    legend_font: ImageFont = Find.image_font(36, True)
    legend_height: int = legend_font.getsize(tallest_word)[1]
    legend_color: tuple = (0, 0, 0, 255)
    legend_padding: int = 15

    message_font_size: int = 90
    message_padding: int = 30
    message_right_spacing: int = -50

    message_title_state: bool = True
    message_title_font: ImageFont = Find.image_font(message_font_size, message_title_state)
    message_title_height: int = legend_title_font.getsize(tallest_word)[1]
    message_title_color: tuple = (2, 129, 56, 255)

    message_subtitle_state: bool = False
    message_subtitle_font: ImageFont = Find.image_font(message_font_size // 3, message_subtitle_state)
    message_subtitle_height: int = legend_font.getsize(tallest_word)[1]
    message_subtitle_color: tuple = (2, 129, 56, 255)

    message_title_special_font: ImageFont = Find.image_font(message_font_size, use_unicode = True)
    message_subtitle_special_font: ImageFont = Find.image_font(message_font_size // 3, use_unicode = True)

    day_label_font: ImageFont = Find.image_font(day_font_size >> 1, True)
    day_label_color: tuple = (2, 129, 56, 255)
