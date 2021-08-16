import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "monthly_calendar"))

from monthly_calendar.Month_Calendar import Monthly_Calendar
from monthly_calendar.attributes import Calendar_Settings
from monthly_calendar.classes import Event
import Find
# --- #

b = Calendar_Settings(
    title = "Plans for the Month of",
    message_of_the_month = True,
    message_title = "Mentions:",
    message_subtitle = "13 = Birthday, 19 = Meeting"
    # allowed_events = tuple(Find.all_events(filter_mode_name = ["4"])) # has to be tuple cause I was using dataclasses, filters out all of the events with this type, 4 is a special that will become 1/4 of the image size
)

# in resources folder, the format of the names of the images is {order in legend!priority!shortcut name}Description in Legend.png

events = [
    Event("F", "u", b, custom = -1),
    Event("block", "we", b, [1, 2, 3], custom = ["4"]),
    Event("labeled", "we", b, custom = "Rest day!"),
    Event("labeled", "wd", b, custom = "Work"),
    Event("labeled", "d", b, [21, 28], custom = "Family"),
    Event("B", "d", b, [13, 19], custom = "Work")
    ]

a = Monthly_Calendar(b)
a.add_events(events)
a.save("test2.png")




