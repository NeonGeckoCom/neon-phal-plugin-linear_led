# PHAL Linear LED Plugin
Enables interaction with LEDs in a one-dimensional physical arrangement.

## Standard LED Events
There are default LED animations that are shown when certain things happen. Note
that some of these behaviors are configurable while others are hard-coded so
users can be confident they know the device's state.

### Listening
This will always be a breathing animation. The color may be specified in settings
or will default to the theme color (same as the screen border when listening).

### Sleeping
This will always be a static LED ring color. The color may be specified in
settings or will default to Red.

### Muted
This will always be a static LED ring color. The color may be specified in
settings or will default to Burnt Orange.

### Microphone Muted Error
This will flash all LEDs 3 times in the microphone muted color. This happens if
the user tries to start listening while the mic is muted.

### Speech Input Error
This will flash all LEDs 1 time in the error color (default Red). The color may
be specified in settings.

### Skill Intent Error
This will flash all LEDs 4 times in the error color (default Red). The color may
be specified in settings.

### Utterance sent to skills
This is disabled by default, but when enabled will provide an animation in the
theme color when an utterance is emitted.

### Skill intent handler start
This is disabled by default, but when enabled will provide an animation in the
theme color when a skill intent starts.

## Configuration
For Neopixel devices, the plugin requires `root` permissions and must be enabled
explicitly in the system configuration in `/etc`.
```yaml
PHAL:
  admin:
    neon-phal-plugin-linear-led-neopixel:
      enabled: true
```
>*Note*: If any other config is present here (i.e. colors), it will override 
> all configuration in `PHAL.neon-phal-plugin-linear-led` for Neopixel devices.
> It is recommended to not include config here so that it applies to all linear
> LED classes.

### Colors
By default, the plugin will use theme colors for different events, but these
colors may also be overridden in configuration.
```yaml
PHAL:
  neon-phal-plugin-linear-led:
    listen_color: white
    mute_color: burnt_orange
    sleep_color: red
    error_color: red
```

### Optional Event Animations
There are standard messagebus events that you can choose to show animations for.
These are disabled by default, but may be desirable to provide more user feedback
or troubleshoot specific error cases.
```yaml
PHAL:
  neon-phal-plugin-linear-led:
    utterance_animation: refill
    handler_animation: bounce
```

## messagebus API
This plugin exposes messagebus listener `neon.linear_led.show_animation` to 
trigger showing an animation. Any skill, plugin, or other integration can 
request an LED ring animation by emitting a Message:
```python
from mycroft_bus_client import Message

Message("neon.linear_led.show_animation",
        {'animation': 'chase',
         'color': 'green',
         'timeout': 10})
```

Note that the plugin may enforce a limit to how long the animation is displayed
and also may replace the animation with a different one that is triggered.