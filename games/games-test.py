import asyncio

from games.sound import Notes
from games.shake import Shake

fred = Notes()

class SimplePlushie:
    def __init__(self):
        self.running = True
        
george = SimplePlushie()

async def main(code):
    task = asyncio.create_task(code.run(george))
    for i in range(5):
        print('@',end='')
        await asyncio.sleep(1)
    george.running = False
    print('ending game')
    await task

    
asyncio.run(main(fred))
bill = Shake()
asyncio.run(main(bill))