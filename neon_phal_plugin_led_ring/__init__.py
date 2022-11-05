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
from abstract_hardware_interface.led import Color, AbstractLed
from abstract_hardware_interface.led.animations import BreatheLedAnimation, \
    LoopFillLedAnimation, animations, LedAnimation


class LedRing(PHALPlugin):
    def __init__(self, led: AbstractLed, bus=None, config=None, name=None):
        PHALPlugin.__init__(self, bus=bus, name=name, config=config)
        self.leds = led
        self.leds.fill(Color.BLACK.as_rgb_tuple())

        self.listen_color = Color.WHITE
        self.mute_color = Color.BURNT_ORANGE
        self.sleep_color = Color.RED
        self.init_settings()

        self._led_lock = RLock()
        self.listen_timeout_sec = 30

        self._listen_animation = BreatheLedAnimation(self.leds,
                                                     self.listen_color)

        self._mute_animation = LoopFillLedAnimation(self.leds, self.mute_color)
        self._unmute_animation = LoopFillLedAnimation(self.leds, Color.BLACK,
                                                      True)

        self._sleep_animation = LoopFillLedAnimation(self.leds,
                                                     self.sleep_color)
        self._awake_animation = LoopFillLedAnimation(self.leds, Color.BLACK,
                                                     True)

        self.register_listeners()

        # Check mic switch status
        self.bus.emit(Message('mycroft.mic.status'))

    def init_settings(self):
        """
        Safely initialize LED color settings from config.
        """
        try:
            self.listen_color = Color.from_name(
                self.config.get('listen_color') or 'white')
        except ValueError:
            LOG.warning(f'invalid color in config: '
                        f'{self.config.get("listen_color")}')
            self.listen_color = Color.WHITE

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
        self.bus.on('mycroft.volume.increase', self.on_volume_increase)
        self.bus.on('mycroft.volume.decrease', self.on_volume_decrease)
        self.bus.on('neon.led_ring.show_animation', self.on_show_animation)

    def on_show_animation(self, message):
        animation_name = message.data.get('animation')
        color_name = message.data.get('color')
        timeout = message.data.get('timeout', 5)
        color = Color.from_name(color_name)
        animation: LedAnimation = animations[animation_name](self.leds, color)
        with self._led_lock:
            animation.start(timeout)
            animation.stop()

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
