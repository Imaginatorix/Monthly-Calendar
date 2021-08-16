from PIL import Image, ImageDraw
import Find
import calendar

class Month_Grid():
    def __init__(self, settings, style):
        self.settings = settings
        self.style = style
        
        self.cal = calendar.Calendar(self.settings.day_start)
        self.month_days = self.cal.monthdayscalendar(self.settings.year, self.settings.month)

        self.customize_style()

    def customize_style(self):
        # month_title_height
        month_title = ""
        if self.settings.show_month:
            month_title += Month_Grid.month_name(self.settings.month)
        if self.settings.show_year:
            month_title += f" {self.settings.year}" if len(month_title) > 0 else str(self.settings.year)

        self.style.month_title_height = Find.font_height(self.style.month_title_font, month_title)
        # ---

    def draw_grid(self, events = None):
        day_from, day_to = (self.settings.day_start, self.settings.day_start + 6) # x-axis
        day_count = (day_to - day_from) + 1
        week_from, week_to = (0, len(self.month_days)) # y-axis
        week_count = week_to - week_from
        grid_width = day_count * self.style.day_width
        grid_height = week_count * self.style.day_height
        above_grid_height = self.style.month_title_height + self.style.day_title_box_padding + self.style.day_title_height # + self.style.pad_y
        size = (grid_width + (2 * self.style.pad_x), grid_height + above_grid_height + (self.style.line_x_width >> 1))

        self.IMAGE = Image.new("RGBA", size, self.style.image_bg)
        self.write = ImageDraw.Draw(self.IMAGE)

        # write month calendar title
        month_title = ""
        if self.settings.show_month:
            month_title += Month_Grid.month_name(self.settings.month)
        if self.settings.show_year:
            month_title += f" {self.settings.year}" if len(month_title) > 0 else str(self.settings.year)
        x = size[0] / 2
        y = (self.style.month_title_height >> 1) # + self.style.pad_y
        self.write.text((x, y), month_title, anchor = "mm", font = self.style.month_title_font, fill = self.style.month_title_color)

        # horizontal lines
        x = (self.style.pad_x, self.style.pad_x + grid_width)
        for i in range(week_count + 1):
            y = above_grid_height + (i * self.style.day_height)
            self.write.line([(x[0], y), (x[1], y)], fill = self.style.line_x_color, width = self.style.line_x_width)

        # vertical lines
        y = (above_grid_height - self.style.day_title_height, above_grid_height + grid_height)
        for i in range(day_count + 1):
            x = self.style.pad_x + (i * self.style.day_width)
            self.write.line([(x, y[0]), (x, y[1])], fill = self.style.line_y_color, width = self.style.line_y_width)

        # box for day name
        start_coord = (self.style.pad_x - (self.style.line_y_width >> 1), above_grid_height - self.style.day_title_height)
        end_coord = (self.style.pad_x + grid_width + (self.style.line_y_width >> 1), above_grid_height)
        self.write.rectangle((start_coord, end_coord), fill = self.style.day_title_box_color)

        # write name of the day
        for i in range(day_count):
            day = day_from + i
            text = Month_Grid.day_title(day, self.settings.day_name_length)
            x = self.style.pad_x + (i * self.style.day_width) + (self.style.day_width / 2)
            y = (above_grid_height - self.style.day_title_height) + (self.style.day_title_height / 2)
            color = self.style.day_title_color_weekend if (text == "Saturday"[0:self.settings.day_name_length] or text == "Sunday"[0:self.settings.day_name_length]) else self.style.day_title_color_weekday
            self.write.text((x, y), text, anchor = "mm", font = self.style.day_title_font, fill = color)

        # write day number in boxes
        for a, week in zip(range(len(self.month_days)), self.month_days):
            for b, day in zip(range(len(week)), week):
                if day != 0:
                    x = self.style.pad_x + (b * self.style.day_width) + (self.style.day_width / 2)
                    y = above_grid_height + (a * self.style.day_height) + (self.style.day_height / 2)
                    color = self.style.day_color_weekend if (Month_Grid.day_title(day_from + b) == "Saturday" or Month_Grid.day_title(day_from + b) == "Sunday") else self.style.day_color_weekday
                    self.write.text((x, y), str(day), anchor = "mm", font = self.style.day_font, fill = color)
                    
                    if events is not None:
                        day_attributes = events[day]
                        if day_attributes["Labeled"]:
                            y += (self.style.day_height >> 2)
                            self.write.text((x, y), day_attributes["Label"], anchor = "mt", font = self.style.day_label_font, fill = self.style.day_label_color)
                        if day_attributes["Type"] is not None:
                            if day_attributes["Type"].mode_name != "4": # 4 is special case, I need to add support to it, but now, consider it as special
                                new_size_tuple = (self.style.day_width - (2 * self.style.line_y_width), self.style.day_height - (2 * self.style.line_x_width))
                                image = Image.open(day_attributes["Type"].path)
                                size_Find = Find.compute_new_size(image, new_size_tuple, include_side = True)
                                image = image.resize(size_Find[0])
                                x = self.style.pad_x + (b * self.style.day_width) + ((self.style.day_width - image.size[0]) >> 1) + (self.style.line_y_width * (size_Find[1] == 0))
                                y = above_grid_height + (a * self.style.day_height) + (self.style.line_x_width * (size_Find[1] == 1))
                                self.IMAGE.paste(image, (x, y))
                            else:
                                new_size_tuple = ((self.style.day_width - (2 * self.style.line_y_width)) >> 1, (self.style.day_height - (2 * self.style.line_x_width)) >> 1)
                                image = Image.open(day_attributes["Type"].path)
                                size_Find = Find.compute_new_size(image, new_size_tuple, include_side = True)
                                image = image.resize(size_Find[0])
                                x = self.style.pad_x + (b * self.style.day_width) + ((3 * self.style.day_width) >> 2) - int(self.style.line_y_width * (1.5))
                                y = above_grid_height + (a * self.style.day_height) + (self.style.day_height >> 1) + (self.style.line_x_width >> 1)
                                self.IMAGE.paste(image, (x, y))

    def get_image(self):
        return self.IMAGE

    @staticmethod
    def day_title(day, length = None):
        day %= 7
        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return day_name[day][0:length]

    @staticmethod
    def month_name(number):
        number -= 1
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        return months[number]



