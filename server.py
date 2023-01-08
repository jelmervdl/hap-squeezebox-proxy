#!/usr/bin/env python3
import sys
import signal
import asyncio
import logging
from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_PROGRAMMABLE_SWITCH
from aiohttp.web import _run_app, Application, FileResponse, access_logger
from functools import partial


class Switch(Accessory):
	category = CATEGORY_PROGRAMMABLE_SWITCH

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		switch = self.add_preload_service('StatelessProgrammableSwitch', chars=['ProgrammableSwitchEvent'])
		self._char_event = switch.configure_char('ProgrammableSwitchEvent', value=0, valid_values={"SinglePress": 0})


async def switch_handler(request, *, switch):
	# print(f"{request.method} {request.http_range!r}")
	if request.http_range == slice(None, None, 1):
		switch._char_event.set_value(0)
	return FileResponse('yay.mp3')


if __name__ == "__main__":
	driver = AccessoryDriver(port=51828)

	webapp = Application()
	
	bridge = Bridge(driver, 'Bridge')
	driver.add_accessory(accessory=bridge)
	
	for n in range(1, 4):
		switch = Switch(driver, f'Radio {n}')
		bridge.add_accessory(switch)
		webapp.router.add_get(f'/switch{n}', partial(switch_handler, switch=switch))

	access_logger.setLevel(logging.DEBUG)
	access_logger.addHandler(logging.StreamHandler())
	driver.add_job(_run_app(webapp, host='0.0.0.0', port=8080, print=None, access_log=access_logger))

	signal.signal(signal.SIGTERM, driver.signal_handler)
	driver.start()
