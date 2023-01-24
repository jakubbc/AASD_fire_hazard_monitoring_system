import datetime
import time
import random

from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class ExtinguisherDroneAgent(agent.Agent):
    class ReceiveMessExtinguisherRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('[{}]    Agent [{}]    received a {} message: \'{}\''.format(datetime.datetime.now().time(),
                                                                                   str(self.agent.jid).split('@')[0],
                                                                                   msg.get_metadata('type'),
                                                                                   msg.body))
                # fly to target
                time.sleep(1)
                # extinguish
                time.sleep(2)
                # send info to camera drone
                fire_rand = random.uniform(0, 1)
                if fire_rand <= 0:
                    self.agent.add_behaviour(self.agent.SendMessExtinguisherConfirmation())
                # fly to base
                time.sleep(1)

    class SendMessExtinguisherConfirmation(OneShotBehaviour):
        async def run(self):
            msg = Message(to='camera1@jabbers.one')
            msg.set_metadata("type", "extinguisherConfirmation")
            msg.body = 'done'
            await self.send(msg)

    async def setup(self):
        template = Template()
        template.set_metadata("type", "extinguisherRequest")
        self.add_behaviour(self.ReceiveMessExtinguisherRequest(), template)
        print("Agent {} initialized".format(str(self.jid).split('@')[0]))
