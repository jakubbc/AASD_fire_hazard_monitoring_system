import time
import json
import datetime
import Agents.Constants as Constants

from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template


class SentryAgent(agent.Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False, ):
        super().__init__(jid, password, verify_security)

    class MonitoringService(PeriodicBehaviour):
        async def run(self):
            response = Message(str(self.mySelf))  # Instantiate the message
            response.set_metadata("type", "measurementRequest")  # Set the "inform" FIPA performative
            await self.send(response)

    class ProcessingService(CyclicBehaviour):

        async def run(self):
            results = await self.receive()
            if results is not None and self.processMeasurements(json.loads(results.body)):
                self.agent.add_behaviour(self.agent.CheckNeighbours(self.get("neighbors")))
            else:
                print("not fire")

        def processMeasurements(self, results):
            isFire = 0
            if results["temperature"] > Constants.TemperatureThreshold:
                isFire += 1
            if results["humidity"] > Constants.HumidityThreshold:
                isFire += 1
            if results["co2"] > Constants.Co2Threshold:
                isFire += 1
            if results["wind"] > Constants.WindThreshold:
                isFire += 1

            if isFire > 2:
                return True
            else:
                return False

    class SendMeasurementsService(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  # wait for message for <timeout> seconds
            if msg:
                response = Message(to=str(msg.sender))  # Instantiate the message
                response.set_metadata("type", "measurementResponse")  # Set the "inform" FIPA performative
                # TODO
                response.body = ' {"temperature": 30,"humidity": 15,"co2": 79,"wind": 14}'  # Set the message content
                await self.send(response)

    class CheckNeighbours(OneShotBehaviour):
        async def run(self):
            for neighbor in self.get('neighbors'):
                print("sending to: " + neighbor)
                msg = Message(to=neighbor)
                msg.set_metadata("type", "measurementRequest")
                await self.send(msg)

    class NeighbourResponseService(CyclicBehaviour):

        async def run(self):
            print("check sasiadow")
            msg = await self.receive(timeout=100)
            print(msg)
            # if msg:
            #     self.neighborResults.append(msg.body)
            # if len(self.neighbors) == len(self.neighborResults):
            #     # TODO upgrade processing
            #     positiveCount = 0
            #     for result in self.neighborResults:
            #         jsonObject = json.loads(result)
            #         if jsonObject["temperature"] > 100:
            #             positiveCount += 1
            #
            #     if positiveCount > self.neighborResults.len() / 2:
            #         msg = Message(to='camera1@jabbers.one')
            #         msg.set_metadata("type", "cameraRequest")
            #         # TODO make coordinate parameter
            #         msg.body = '1'
            #         await self.send(msg)
            #     else:
            #         msg = Message(to='camera1@jabbers.one')
            #         msg.set_metadata("type", "faultySentry")
            #         msg.body = self.jid
            #         await self.send(msg)
            #         self.neighborResults = []  # reset results

    async def setup(self):
        startAt = datetime.datetime.now() + datetime.timedelta(seconds=2)
        self.add_behaviour(self.MonitoringService(period=2, startAt=startAt))

        template = Template()  # Respond to other Sentries with local measurements
        template.set_metadata("type", "measurementRequest")
        self.add_behaviour(self.SendMeasurementsService(), template)

        template = Template()  # Respond to other Sentries with local measurements
        template.set_metadata("type", "measurementResponse")
        # template.set_sender(self.jid)
        self.add_behaviour(self.ProcessingService(), template)

        template = Template()  # Recieve responses from other agents
        template.set_metadata("type", "measurementResponses")
        self.add_behaviour(self.NeighbourResponseService(), template)

        print("Agent {} initialized".format(str(self.jid).split('@')[0]))
