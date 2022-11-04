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

from ovos_utils.log import LOG
from ovos_plugin_manager.templates.phal import PHALPlugin
from abstract_hardware_interface.led import Color, AbstractLed
from abstract_hardware_interface.led.animations import BreatheLedAnimation,\
    LoopFillLedAnimation


class LedRing(PHALPlugin):
    def __init__(self, led: AbstractLed, bus=None, config=None, name=None):
        PHALPlugin.__init__(self, bus=bus, name=name, config=config)
        self.leds = led
        self.leds.fill(Color.BLACK)

        self.listen_color = Color.WHITE
        self.mute_color = Color.BURNT_ORANGE
        self.sleep_color = Color.RED

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

    def register_listeners(self):
        self.bus.on('mycroft.mic.mute', self.on_mic_mute)
        self.bus.on('mycroft.mic.unmute', self.on_mic_unmute)
        self.bus.on('mycroft.volume.increase', self.on_volume_increase)
        self.bus.on('mycroft.volume.decrease', self.on_volume_decrease)

    def on_mic_mute(self, message):
        LOG.debug('muted')
        self._mute_animation.start()

    def on_mic_unmute(self, message):
        LOG.debug('unmuted')
        self._unmute_animation.start()

    def on_volume_increase(self, message):
        # TODO: Get volume and fill LEDs accordingly
        pass

    def on_volume_decrease(self, message):
        # TODO: Get volume and fill LEDs accordingly
        pass

    def on_record_begin(self, message=None):
        LOG.debug('record begin')
        self._listen_animation.start(self.listen_timeout_sec)

    def on_record_end(self, message=None):
        LOG.debug('record end')
        self._listen_animation.stop()

    def on_awake(self, message=None):
        self._awake_animation.start()

    def on_sleep(self, message=None):
        self._sleep_animation.start()

    def on_reset(self, message=None):
        self.leds.fill(Color.BLACK)

    def on_system_reset(self, message=None):
        self.leds.fill(Color.BLACK)

    def shutdown(self):
        self.leds.fill(Color.BLACK)
