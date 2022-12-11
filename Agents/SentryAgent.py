import time
import json

from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class SentryAgent(agent.Agent):
    def __init__(self, jid: str, password: str, neighbors: [], verify_security: bool = False, ):
        super().__init__(jid, password, verify_security)
        self.neighbors = neighbors

        class MonitoringService(CyclicBehaviour):
            def __init__(self, jid, neighbors):
                super().__init__()
                self.mySelf = jid + "@jabbers.one"
                self.neighbors = neighbors

            async def run(self):
                if self.processMeasurements():
                    self.agent.add_behaviour(self.agent.CheckNeighbours(neighbors))
                else:
                    time.sleep(1)

            def processMeasurements(self): #Return True if is fire, Flase otherwise
                isFire = True
                # TODO some processing
                if isFire:
                    return True
                else:
                    return False

        class SendMeasurementsService(CyclicBehaviour):
            async def run(self):
                msg = await self.receive()  # wait for message for <timeout> seconds
                if msg:
                    response = Message(to=msg.sender)  # Instantiate the message
                    response.set_metadata("type", "measurementResponse")  # Set the "inform" FIPA performative
                    # TODO
                    response.body = ' "temperature" : 100 }'  # Set the message content
                    await self.send(response)

        class CheckNeighbours(OneShotBehaviour):
            def __init__(self, neighbors):
                super().__init__()
                self.neighbors = neighbors

            async def run(self):
                for neighbor in neighbors:
                    msg = Message(to=neighbor)
                    msg.set_metadata("type", "measurementRequest")
                    await self.send(msg)

        class NeighbourResponseService(CyclicBehaviour):
            def __init__(self, neighbors):
                super().__init__()
                self.neighborResults = []
                self.neighbors = neighbors

            async def run(self):
                msg = await self.receive()
                if msg:
                    self.neighborResults.append(msg.body)
                if self.neighbors.len() == self.neighborResults.len():
                    #TODO upgrade processing
                    positiveCount = 0
                    for result in self.neighborResults:
                        jsonObject = json.loads(result)
                        if jsonObject["temperature"] > 100:
                            positiveCount += 1

                    if positiveCount > self.neighborResults.len()/2:
                        msg = Message(to='camera1@jabbers.one')
                        msg.set_metadata("type", "cameraRequest")
                        # TODO make coordinate parameter
                        msg.body = '1'
                        await self.send(msg)
                    else:
                        msg = Message(to='camera1@jabbers.one')
                        msg.set_metadata("type", "faultySentry")
                        msg.body = self.jid
                        await self.send(msg)
                self.neighborResults = [] #reset results

        async def setup(self):
            self.add_behaviour(self.MonitoringService(self.jid, self.neighbors))

            template = Template() #Respond to other Sentries with local measurements
            template.set_metadata("type", "measurementRequest")
            self.add_behaviour(self.SendMeasurementsService(), template)

            template = Template()  # Recieve responses from other agents
            template.set_metadata("type", "measurementResponse")
            self.add_behaviour(self.NeighbourResponseService(self.neighbors), template)

            print("Agent {} initialized".format(str(self.jid).split('@')[0]))
