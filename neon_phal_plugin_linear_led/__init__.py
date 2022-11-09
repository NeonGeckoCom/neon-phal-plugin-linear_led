# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from threading import RLock

from mycroft_bus_client import Message
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.phal import PHALPlugin
from ovos_plugin_manager.hardware.led import Color, AbstractLed
from ovos_plugin_manager.hardware.led.animations import BreatheLedAnimation, \
    FillLedAnimation, BlinkLedAnimation, animations, LedAnimation


class LinearLed(PHALPlugin):
    def __init__(self, led: AbstractLed, bus=None, config=None, name=None):
        PHALPlugin.__init__(self, bus=bus, name=name, config=config)
        self.leds = led
        self.leds.fill(Color.BLACK.as_rgb_tuple())

        self.listen_color = Color.THEME
        self.mute_color = Color.BURNT_ORANGE
        self.sleep_color = Color.RED
        self.init_settings()

        self._led_lock = RLock()
        self.listen_timeout_sec = 30

        self._listen_animation = BreatheLedAnimation(self.leds,
                                                     self.listen_color)

        self._mute_animation = FillLedAnimation(self.leds, self.mute_color)
        self._unmute_animation = FillLedAnimation(self.leds, Color.BLACK,
                                                  True)

        self._sleep_animation = FillLedAnimation(self.leds,
                                                 self.sleep_color)
        self._awake_animation = FillLedAnimation(self.leds, Color.BLACK,
                                                 True)

        self._mic_muted_animation = BlinkLedAnimation(self.leds,
                                                      self.mute_color,
                                                      3, False)

        self.register_listeners()

        # Get theme colors
        self.bus.emit(Message('ovos.theme.get'))

        # Check mic switch status
        self.bus.emit(Message('mycroft.mic.status'))

        # TODO: Define a queue for animations to handle synchronous animations
        #       and restoring persistent states

    def init_settings(self):
        """
        Safely initialize LED color settings from config.
        """
        try:
            self.listen_color = Color.from_name(
                self.config.get('listen_color') or 'theme')
        except ValueError:
            LOG.warning(f'invalid color in config: '
                        f'{self.config.get("listen_color")}')
            self.listen_color = Color.THEME

        try:
            self.mute_color = Color.from_name(
                self.config.get('mute_color') or 'burnt_orange')
        except ValueError:
            LOG.warning(f'invalid color in config: '
                        f'{self.config.get("mute_color")}')
            self.listen_color = Color.BURNT_ORANGE

        try:
            self.sleep_color = Color.from_name(
                self.config.get('sleep_color') or 'red')
        except ValueError:
            LOG.warning(f'invalid color in config: '
                        f'{self.config.get("sleep_color")}')
            self.listen_color = Color.RED

    def register_listeners(self):
        self.bus.on('mycroft.mic.mute', self.on_mic_mute)
        self.bus.on('mycroft.mic.unmute', self.on_mic_unmute)
        self.bus.on('mycroft.mic.error', self.on_mic_error)
        self.bus.on('mycroft.volume.increase', self.on_volume_increase)
        self.bus.on('mycroft.volume.decrease', self.on_volume_decrease)
        self.bus.on('neon.linear_led.show_animation', self.on_show_animation)
        self.bus.on('ovos.theme.get.response', self.on_theme_update)
        # TODO: Define method to stop any active/queued animations

    def on_theme_update(self, message):
        LOG.debug(f"Updating theme color(s): {message.data}")
        try:
            color = message.data.get('secondaryColor')
            Color.set_theme(color)
            LOG.debug(f'LED Theme color set to {Color.THEME.as_rgb_tuple()}')
        except Exception as e:
            LOG.exception(e)

    def on_show_animation(self, message):
        animation_name = message.data.get('animation')
        color_name = message.data.get('color')
        timeout = message.data.get('timeout', 5)
        color = Color.from_name(color_name)
        LOG.debug(f'showing animation: {animation_name}')
        animation: LedAnimation = animations[animation_name](self.leds, color)
        with self._led_lock:
            animation.start(timeout)
            animation.stop()

    def on_mic_error(self, message):
        err = message.data.get('error')
        LOG.debug(f'mic error: {err}')
        with self._led_lock:
            if err == 'mic_sw_muted':
                self._mic_muted_animation.start()
                self.leds.fill(self.mute_color.as_rgb_tuple())
            else:
                LOG.info(f"unknown mic error: {err}")

    def on_mic_mute(self, message):
        LOG.debug('muted')
        with self._led_lock:
            self._mute_animation.start()

    def on_mic_unmute(self, message):
        LOG.debug('unmuted')
        with self._led_lock:
            self._unmute_animation.start()

    def on_volume_increase(self, message):
        # TODO: Get volume and fill LEDs accordingly
        pass

    def on_volume_decrease(self, message):
        # TODO: Get volume and fill LEDs accordingly
        pass

    def on_record_begin(self, message=None):
        LOG.debug('record begin')
        with self._led_lock:
            self._listen_animation.start(self.listen_timeout_sec)

    def on_record_end(self, message=None):
        LOG.debug('record end')
        self._listen_animation.stop()

    def on_awake(self, message=None):
        with self._led_lock:
            self._awake_animation.start()

    def on_sleep(self, message=None):
        with self._led_lock:
            self._sleep_animation.start()

    def on_reset(self, message=None):
        self.leds.fill(Color.BLACK.as_rgb_tuple())

    def on_system_reset(self, message=None):
        self.leds.fill(Color.BLACK.as_rgb_tuple())

    def shutdown(self):
        self.leds.fill(Color.BLACK.as_rgb_tuple())
