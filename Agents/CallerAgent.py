import time

from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class CallerAgent(agent.Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        # custom fields defined here
        self.camera_drone_available = True  # state of the camera drone to determine if drone can be sent
        self.fire_brigade_called = False  # was 911 already called?
        self.faulty_sentries = []  # list of sentries with faulty sensors for human user

    class ReceiveMessCallEmergency(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
                # call 911 and set flag
                if not self.agent.fire_brigade_called:
                    time.sleep(2)
                    print('Agent {}: called 911!'.format(str(self.agent.jid).split('@')[0]))
                    self.agent.fire_brigade_called = True
                else:
                    print('Agent {}: 911 already called!'.format(str(self.agent.jid).split('@')[0]))

    class ReceiveMessSmallFire(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
                # call camera drone if it's available
                if self.agent.camera_drone_available:
                    self.agent.add_behaviour(self.agent.SendMessCameraRequest())
                    self.agent.camera_drone_available = False
                else:
                    print('Agent {}: drone already in use!'.format(str(self.agent.jid).split('@')[0]))

    class ReceiveMessCameraFree(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
                self.agent.camera_drone_available = True

    class ReceiveMessFaultySentry(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                print('Agent {} received a {} message: \'{}\''.format(str(self.agent.jid).split('@')[0],
                                                                      msg.get_metadata('type'), msg.body))
                self.agent.faulty_sentries.append(str(msg.body))
                print(f'List of faulty sentries: self.agent.faulty_sentries')

    class SendMessCameraRequest(OneShotBehaviour):
        async def run(self):
            msg = Message(to='camera1@jabbers.one')
            msg.set_metadata("type", "cameraRequest")
            # send id of station requesting drone (serving as coordinates)
            # TODO make coordinate parameter
            msg.body = '1'
            await self.send(msg)

    async def setup(self):
        template = Template()
        template.set_metadata("type", "callEmergency")
        self.add_behaviour(self.ReceiveMessCallEmergency(), template)

        template = Template()
        template.set_metadata("type", "smallFire")
        self.add_behaviour(self.ReceiveMessSmallFire(), template)

        template = Template()
        template.set_metadata("type", "cameraFree")
        self.add_behaviour(self.ReceiveMessCameraFree(), template)

        template = Template()
        template.set_metadata("type", "faultySentry")
        self.add_behaviour(self.ReceiveMessFaultySentry(), template)

        print("Agent {} initialized".format(str(self.jid).split('@')[0]))
