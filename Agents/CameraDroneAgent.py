import random
import time
import datetime

from spade import agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class CameraDroneAgent(agent.Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        # custom fields defined here
        self.served_sentry = ''
    class ReceiveMessCameraRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                self.agent.served_sentry = msg.body
                print('[{}]    Agent [{}]    received a {} message: \'{}\''
                      .format(datetime.datetime.now().time(),
                              str(self.agent.jid).split('@')[0],
                              msg.get_metadata('type'),
                              self.agent.served_sentry))
                # fly to sentry
                time.sleep(1)
                # simulate checking for fire
                fire_rand = random.uniform(0, 1)
                if fire_rand <= 0:  # probability of no fire in simulation
                    # call extinguisher drone
                    self.agent.add_behaviour(self.agent.SendMessExtinguisherRequest())
                    # wait for confirmation from extinguisher that fire was extinguished
                    template = Template()
                    template.set_metadata("type", "extinguisherConfirmation")
                    self.agent.add_behaviour(self.agent.ReceiveMessExtinguisherConfirmation(), template)
                else:
                    # inform caller that sentry has faulty sensor
                    self.agent.add_behaviour(self.agent.SendMessFaultySentry())
                    # fly back to base
                    time.sleep(1)
                    # inform caller that camera drone is free
                    self.agent.add_behaviour(self.agent.SendMessCameraFree())

    class ReceiveMessExtinguisherConfirmation(OneShotBehaviour):
        async def run(self):
            msg = await self.receive(timeout=15)  # wait for message for <timeout> seconds
            if msg:
                print('[{}]    Agent [{}]    received a {} message: \'{}\''
                      .format(datetime.datetime.now().time(),
                              str(self.agent.jid).split('@')[0],
                              msg.get_metadata('type'),
                              msg.body))
            else:
                self.agent.add_behaviour(self.agent.SendMessCallEmergency())
            # fly back to base
            time.sleep(1)
            # inform caller that camera drone is free
            self.agent.add_behaviour(self.agent.SendMessCameraFree())

    class SendMessExtinguisherRequest(OneShotBehaviour):
        async def run(self):
            msg = Message(to='extinguisher1@jabbers.one')
            msg.set_metadata("type", "extinguisherRequest")
            msg.body = self.agent.served_sentry
            await self.send(msg)

    class SendMessCallEmergency(OneShotBehaviour):
        async def run(self):
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "callEmergency")
            msg.body = self.agent.served_sentry
            await self.send(msg)

    class SendMessCameraFree(OneShotBehaviour):
        async def run(self):
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "cameraFree")
            msg.body = 'done'
            await self.send(msg)

    class SendMessFaultySentry(OneShotBehaviour):
        async def run(self):
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "faultySentry")
            msg.body = self.agent.served_sentry
            await self.send(msg)

    async def setup(self):
        template = Template()
        template.set_metadata("type", "cameraRequest")
        self.add_behaviour(self.ReceiveMessCameraRequest(), template)

        print("Agent {} initialized".format(str(self.jid).split('@')[0]))
