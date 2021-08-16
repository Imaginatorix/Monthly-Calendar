from PIL import Image, ImageFont
from fontTools.ttLib import TTFont
from classes import Day_Type
import os

def get_resource_path():
    prev_path = os.getcwd()

    os.chdir("monthly_calendar/resources")
    path = os.getcwd()
    os.chdir(prev_path)

    return path

def font_path(emphasis, resource_path = get_resource_path()):
    prev_path = os.getcwd()
    os.chdir(os.path.join(resource_path, "fonts"))

    font_default = "league-spartan.bold.ttf"
    font_emphasis = "archivo-black.regular.ttf"

    if emphasis:
        font = os.path.join(os.getcwd(), font_emphasis)
    else:
        font = os.path.join(os.getcwd(), font_default)

    os.chdir(prev_path)

    return font

def image_font(size, emphasis = False, use_unicode = False, resource_path = get_resource_path()):
    # Free for commercial use. From https://www.1001fonts.com/league-spartan-font.html and https://www.1001fonts.com/archivo-black-font.html. + https://www.1001fonts.com/quivira-font.html
    prev_path = os.getcwd()
    os.chdir(os.path.join(resource_path, "fonts"))

    font_default = "league-spartan.bold.ttf"
    font_emphasis = "archivo-black.regular.ttf"
    font_unicode = "quivira.regular.otf"

    if use_unicode:
        font = ImageFont.truetype(font_unicode, size)
    elif emphasis:
        font = ImageFont.truetype(font_emphasis, size)
    else:
        font = ImageFont.truetype(font_default, size)

    os.chdir(prev_path)
    return font

def all_tags(tag_first = True):
    tags = ["~s~", "~bs~"]
    meaning = ["/", "\\"]

    if tag_first:
        return dict(zip(tags, meaning))
    return dict(zip(meaning, tags))

def all_events(resource_path = get_resource_path(), filter_mode_name = None):
    tags = all_tags()
    prev_path = os.getcwd()
    os.chdir(resource_path)

    events = []
    for f in os.listdir():
        if f.endswith(".png"):
            order, favorability, mode_name = (0, 0, "")
            word = f[0:-4]
            if word[0] == "{":
                attributes = []
                requested = ""
                for element, i in zip(word, range(len(word))):
                    if element == "!":
                        attributes.append(requested)
                        requested = ""
                    elif element == "}":
                        attributes.append(requested)
                        requested = ""
                        if len(attributes) != 3:
                            raise Exception("Name file format not followed. It should be \{order!favorability!mode name\}filename.png")
                        start = i + 1
                        break
                    else:
                        if element != "{":
                            requested += element
                order, favorability, mode_name = attributes
                word = f[start:-4]

            for tag in tags:
                word = word.replace(tag, tags[tag])
            if filter_mode_name is None or mode_name not in filter_mode_name:
                events.append(Day_Type(word, os.path.join(os.getcwd(), f), int(order), int(favorability), mode_name))

    os.chdir(prev_path)
    return sorted(events)

def font_height(font, word):
    # https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pils-imagefont-class

    # Here, it is exact, while on Calendar_Month_Style, it is the max
    return font.getmetrics()[0] - font.font.getsize(word)[1][1]

def widest_image(resize_to = None, resource_path = get_resource_path()):
    prev_path = os.getcwd()
    os.chdir(resource_path)
    if resize_to is None:
        widest = max([Image.open(f).size[0] for f in os.listdir() if f.endswith(".png")])
    else:
        widest = max([compute_new_size(Image.open(f), resize_to)[0] for f in os.listdir() if f.endswith(".png")])
    os.chdir(prev_path)

    return widest

def compute_new_size(image, new_size, include_side = False):
    difference = tuple(map(lambda i, j: (i - j) * -((i - j) < 0), image.size, new_size))
    side = difference.index(min(difference))
    from_side, to_side = image.size[side], new_size[side]
    percentage = to_side / from_side
    brand_new_size = tuple([int(i * percentage) for i in list(image.size)])
    if include_side:
        return [brand_new_size, side]
    return brand_new_size


def available_in_font(font, character):
    font = TTFont(font)

    for table in font['cmap'].tables:
        if ord(character) in table.cmap.keys():
            return True
    return False

def separate_unicode(font_path, text):
    unicode_text = ""
    pure_string = ""

    for letter in text:
        if not available_in_font(font_path, letter):
            unicode_text += letter
            pure_string += " "
        else:
            unicode_text += " "
            pure_string += letter
    
    return [pure_string, unicode_text]

