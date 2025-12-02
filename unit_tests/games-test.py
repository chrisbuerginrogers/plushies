import asyncio

from games.sound import Notes
from games.shake import Shake
from games.jump import Jump
from games.rainbow import Rainbow

class SimplePlushie:
    def __init__(self):
        self.running = True
        
plush = SimplePlushie()

async def main(code):
    plush.running = True
    code.start()
    task = asyncio.create_task(code.run())
    for i in range(10):
        print('@',end='')
        await asyncio.sleep(1)
    plush.running = False
    await task
    code.close()

fred = Notes(plush)
asyncio.run(main(fred))

bill = Shake(plush)   
asyncio.run(main(bill))

sally = Jump(plush)   
asyncio.run(main(sally))

sam = Rainbow(plush)
asyncio.run(main(sam))

