# PHAL Linear LED Plugin
Enables interaction with LEDs in a one-dimensional physical arrangement.

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