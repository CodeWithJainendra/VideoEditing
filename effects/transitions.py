"""
Transition effects for video clips
"""
from enum import Enum
from typing import Dict, Any


class TransitionType(Enum):
    NONE = "none"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


TRANSITIONS = {
    TransitionType.FADE: {
        "name": "Fade",
        "description": "Fade to/from black",
        "ffmpeg_filter": "fade=t={type}:st={start}:d={duration}"
    },
    TransitionType.DISSOLVE: {
        "name": "Dissolve",
        "description": "Cross dissolve between clips",
        "ffmpeg_filter": "xfade=transition=fade:duration={duration}:offset={offset}"
    },
    TransitionType.WIPE_LEFT: {
        "name": "Wipe Left",
        "description": "Wipe from right to left",
        "ffmpeg_filter": "xfade=transition=wipeleft:duration={duration}:offset={offset}"
    },
    TransitionType.WIPE_RIGHT: {
        "name": "Wipe Right",
        "description": "Wipe from left to right",
        "ffmpeg_filter": "xfade=transition=wiperight:duration={duration}:offset={offset}"
    },
    TransitionType.SLIDE_LEFT: {
        "name": "Slide Left",
        "description": "Slide in from right",
        "ffmpeg_filter": "xfade=transition=slideleft:duration={duration}:offset={offset}"
    },
    TransitionType.SLIDE_RIGHT: {
        "name": "Slide Right",
        "description": "Slide in from left",
        "ffmpeg_filter": "xfade=transition=slideright:duration={duration}:offset={offset}"
    },
    TransitionType.ZOOM_IN: {
        "name": "Zoom In",
        "description": "Zoom into next clip",
        "ffmpeg_filter": "xfade=transition=zoomin:duration={duration}:offset={offset}"
    },
    TransitionType.ZOOM_OUT: {
        "name": "Zoom Out",
        "description": "Zoom out to next clip",
        "ffmpeg_filter": "xfade=transition=zoomout:duration={duration}:offset={offset}"
    }
}


def get_transition(transition_type: TransitionType) -> Dict[str, Any]:
    """Get transition details"""
    return TRANSITIONS.get(transition_type, {})


def get_all_transitions():
    """Get all available transitions"""
    return [(t, v["name"]) for t, v in TRANSITIONS.items()]
