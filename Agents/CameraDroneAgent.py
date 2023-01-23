import random
import time

from spade import agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class CameraDroneAgent(agent.Agent):
    class ReceiveMessCameraRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
                # fly to sentry
                time.sleep(1)
                # simulate checking for fire
                fire_rand = random.uniform(0, 1)
                if fire_rand >= 0:  # probability of no fire in simulation
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
            msg = await self.receive(timeout=120)  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
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
            # TODO send message body based on sentry number param
            msg.body = '1'
            await self.send(msg)
            # await self.agent.stop()  # this line terminates agent

    class SendMessCallEmergency(OneShotBehaviour):
        async def run(self):
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "callEmergency")
            # TODO send id of station requesting drone (serving as coordinates)
            msg.body = '1'
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
            # TODO send message body based on sentry number param
            msg.body = 'faulty sensor : 1'
            await self.send(msg)

    async def setup(self):
        template = Template()
        template.set_metadata("type", "cameraRequest")
        self.add_behaviour(self.ReceiveMessCameraRequest(), template)

        print("Agent {} initialized".format(str(self.jid).split('@')[0]))
