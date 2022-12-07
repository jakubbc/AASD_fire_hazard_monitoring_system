import time

from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message


class TestAgent(agent.Agent):
    """ Agent for testing other agents' responses"""

    class SendMessCallEmergency(OneShotBehaviour):
        """ to test ReceiveMessCallEmergency in CallerAgent"""

        async def run(self):
            time.sleep(1)
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "callEmergency")
            # send id of station requesting drone (serving as coordinates)
            msg.body = 'call 911!'
            await self.send(msg)

            time.sleep(2)
            await self.send(msg)

    class SendMessSmallFire(OneShotBehaviour):
        """ to test ReceiveMessSmallFire in CallerAgent"""

        async def run(self):
            time.sleep(1)
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "smallFire")
            # send id of station requesting drone (serving as coordinates)
            msg.body = '1'  # id of sentry - serving as coordinates
            await self.send(msg)

            # optionally send the message again to confirm that caller returns busy state
            # time.sleep(3)
            # await self.send(msg)

    class SendMessCameraFree(OneShotBehaviour):
        """ to test ReceiveMessCameraFree in CallerAgent"""

        async def run(self):
            time.sleep(6)
            msg = Message(to='caller1@jabbers.one')
            msg.set_metadata("type", "cameraFree")
            # send id of station requesting drone (serving as coordinates)
            msg.body = 'camera drone free'
            await self.send(msg)

    async def setup(self):
        self.add_behaviour(self.SendMessSmallFire())
        # self.add_behaviour(self.SendMessCameraFree())
        print("Agent {} initialized".format(str(self.jid).split('@')[0]))


if __name__ == '__main__':

    tester1 = TestAgent("tester1@jabbers.one", "aasd_erif")
    future = tester1.start()
    future.result()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:  # stop program (stop button in PyCharm)
            quit_spade()  # terminate all agents and their processes
            break
    print("Test agent terminated")
