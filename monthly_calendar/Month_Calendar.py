from PIL import Image, ImageDraw
from parts import Month_Grid
from attributes import Calendar_Month_Style
from classes import Event, Day_Type
import Find
import os

class Day():
    def __init__(self, name):
        self.name = name
        self.typing = None
        self.no_typing = False
        self.labeled = False
        self.blocked = []
        self.label = None

    def propose_typing(self, typing, custom = None):
        if not self.no_typing or typing.mode_name not in self.blocked:
            if typing == "clear":
                self.no_typing = True
                self.typing = None
            elif typing == "labeled":
                self.labeled = True
                if custom is None:
                    raise Exception("Labeled must have label")
                self.label = str(custom)
                # requested
                if self.typing is not None and self.typing.mode_name != "4":
                        self.labeled = False
            elif typing == "block":
                if custom is None:
                    raise Exception("Block must block something")
                self.blocked += list(custom)
                if self.typing is not None and self.typing.mode_name in self.blocked:
                    self.typing = None
            elif self.typing is not None:
                if self.typing.favorability < typing.favorability:
                    self.typing = typing
                    # requested
                    if self.typing.mode_name != "4":
                        self.labeled = False
            else:
                self.typing = typing
                # requested
                if self.typing.mode_name != "4":
                    self.labeled = False

class Monthly_Calendar():
    def __init__(self, settings, style = Calendar_Month_Style()):
        self.style = style
        self.settings = settings
        self.events = []

    def add_events(self, events: list):
        possible_events = [i.mode_name for i in self.settings.allowed_events] + ["labeled", "clear", "block"]
        
        for event in events:
            if event.typing in possible_events:
                self.events.append(event)
            else:
                raise Exception("Event not supported")

    def arrange_events(self):
        arranged = {}
        day_types = dict(zip([i.mode_name for i in Find.all_events()], [i for i in Find.all_events()]))
        specials = ["labeled", "clear", "block"]
        specials_with_custom = ["labeled", "block"]
        for day in range(1, Event.number_days(self.settings) + 1):
            day = Day(day)
            for event in self.events:
                if day.name in event.applies_to:
                    if event.typing in specials:
                        if event.typing in specials_with_custom:
                            day.propose_typing(event.typing, event.custom)
                        else:
                            day.propose_typing(event.typing)
                    else:
                        day.propose_typing(day_types[event.typing])
            arranged[day.name] = {"Type": day.typing, "Labeled": day.labeled, "Label": day.label}

        return arranged

    def save(self, filename: str):
        self.build_image()
        self.full_image.save(filename, "PNG")

    def title_image(self):
        width = self.grid.get_image().size[0]
        size = (width, self.style.title_height + self.style.pad_y + self.style.title_padding)

        title_image = Image.new("RGBA", size, self.style.image_bg)
        draw = ImageDraw.Draw(title_image)

        x = width / 2
        y = self.style.pad_y + (self.style.title_height / 2)
        draw.text((x, y), self.settings.title, anchor = "mm", font = self.style.title_font, fill = self.style.title_color)

        return title_image

    def legend_image(self):
        events = list(self.settings.allowed_events)
        width = self.grid.get_image().size[0]
        height = (self.style.legend_title_height + self.style.pad_y + (self.style.legend_padding * (len(events) + self.style.legend_title_show) + (len(events) * self.style.legend_height))) if self.settings.legend else 0
        size = (width, height)

        legend_image = Image.new("RGBA", size, self.style.image_bg)
        draw = ImageDraw.Draw(legend_image)

        if self.settings.legend:
            tags = Find.all_tags(False)
            if self.style.legend_title_show:
                x = self.style.pad_x
                y = self.style.legend_padding
                draw.text((x, y), "Legend: ", font = self.style.legend_title_font, fill = self.style.legend_title_color)

            for event, i in zip(events, range(len(events))):
                x = self.style.pad_x
                y = (self.style.legend_padding * (i + 1 + self.style.legend_title_show) + (i * self.style.legend_height)) + (self.style.legend_title_height * self.style.legend_title_show)

                image = Image.open(event.path)
                image = image.resize(Find.compute_new_size(image, (float("inf"), self.style.legend_height)))
                legend_image.paste(image, (x, y), mask = image)

                x += Find.widest_image((float("inf"), self.style.legend_height))
                draw.text((x, y), f" - {event.name}", font = self.style.legend_font, fill = self.style.legend_color)

        if self.settings.message_of_the_month:
            if self.settings.legend:
                # right
                x = width - (self.style.pad_x + self.style.message_title_font.getsize(self.settings.message_title)[0] + self.style.message_right_spacing)
                anchor = "lt"
            else:
                # middle
                x = width >> 1
                anchor = "mt"
            if self.settings.message_title:
                y = (height - (((self.style.message_title_height // 3) << 2) + self.style.message_padding)) >> 1 if self.settings.message_subtitle else (height - self.style.message_title_height) >> 1
                pure, special = Find.separate_unicode(Find.font_path(self.style.message_title_state), self.settings.message_title)
                draw.text((x, y), pure, anchor = anchor, font = self.style.message_title_font, fill = self.style.message_title_color)
                draw.text((x, y), special, anchor = anchor, font = self.style.message_title_special_font, fill = self.style.message_title_color)

                if self.settings.message_subtitle:
                    y += self.style.message_title_height + self.style.message_padding
                    pure, special = Find.separate_unicode(Find.font_path(self.style.message_subtitle_state), self.settings.message_subtitle)
                    draw.text((x, y), pure, anchor = anchor, font = self.style.message_subtitle_font, fill = self.style.message_subtitle_color)
                    draw.text((x, y), special, anchor = anchor, font = self.style.message_subtitle_special_font, fill = self.style.message_subtitle_color)

        return legend_image

    def build_image(self):
        events = self.arrange_events()

        self.grid = Month_Grid(self.settings, self.style)
        self.style = self.grid.style
        self.grid.draw_grid(events)
        grid_image = self.grid.get_image()
        # ---
        title_image = self.title_image()
        # ---
        legend_image = self.legend_image()
        # ---

        self.full_image = self.combine_image([title_image, grid_image, legend_image], "y")

    @staticmethod
    def combine_image(images: list, side: str):
        """
        images is list of PIL.Image
        side is either 'x' or 'y'; x = horizontal, y = vertical
        combine all images into one.
        """
        if side == "x":
            total_width = 0
            max_height = 0
            for img in images:
                total_width += img.size[0]
                max_height = max(max_height, img.size[1])
            
            # create a new image with the appropriate height and width
            new_img = Image.new("RGBA", (total_width, max_height))

            # Write the contents of the new image
            current_width = 0
            for img in images:
                new_img.paste(img, (current_width, 0))
                current_width += img.size[0]

            return new_img
        elif side == "y":
            total_height = 0
            max_width = 0
            for img in images:
                total_height += img.size[1]
                max_width = max(max_width, img.size[0])
            
            # create a new image with the appropriate height and width
            new_img = Image.new("RGBA", (max_width, total_height))

            # Write the contents of the new image
            current_height = 0
            for img in images:
                new_img.paste(img, (0, current_height))
                current_height += img.size[1]

            # Save the image
            return new_img
        else:
            raise Exception("Invalid argument")


