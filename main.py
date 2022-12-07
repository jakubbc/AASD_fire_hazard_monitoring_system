import time

from spade import quit_spade

from Agents.TestAgent import TestAgent
from Agents.CallerAgent import CallerAgent
from Agents.CameraDroneAgent import CameraDroneAgent
from Agents.ExtinguisherDroneAgent import ExtinguisherDroneAgent

agent_names = [
    # ('tester1', TestAgent),
    ('caller1', CallerAgent),
    ('camera1', CameraDroneAgent),
    ('extinguisher1', ExtinguisherDroneAgent),
]

if __name__ == '__main__':

    # initialize all agents
    for agent_name, agent_type in agent_names:
        agent = agent_type(agent_name+'@jabbers.one', 'aasd_erif')
        future = agent.start()
        # future.result()  # wait for agent to initialize
    time.sleep(2)  # wait long enough to initialize all agents
    print('All agents initialized. System ready to operate.')

    # tester1 = TestAgent("tester1@jabbers.one", "aasd_erif")
    # future = tester1.start()
    # future.result()
    #
    # caller1 = CallerAgent("caller1@jabbers.one", "aasd_erif")
    # future = caller1.start()
    # future.result()
    #
    # camera1 = CameraDroneAgent("camera1@jabbers.one", "aasd_erif")
    # future = camera1.start()
    # future.result()
    #
    # extinguisher1 = ExtinguisherDroneAgent("extinguisher1@jabbers.one", "aasd_erif")
    # future = extinguisher1.start()
    # future.result()  # wait for agent to initialize

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:  # stop program (stop button in PyCharm)
            quit_spade()  # terminate all agents and their processes
            break
    print("Agents terminated")
