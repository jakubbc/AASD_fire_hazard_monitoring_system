import time

from spade import quit_spade

from Agents.TestAgent import TestAgent
from Agents.CallerAgent import CallerAgent
from Agents.SentryAgent import SentryAgent
from Agents.CameraDroneAgent import CameraDroneAgent
from Agents.ExtinguisherDroneAgent import ExtinguisherDroneAgent

agent_names = [
    # ('tester1', TestAgent),
    ('caller1', CallerAgent),
    ('camera1', CameraDroneAgent),
    ('extinguisher1', ExtinguisherDroneAgent),
]
sentries = [ #name, logs, neighbors
    ('sentry1', True, ["sentry2@jabbers.one", "sentry3@jabbers.one"]),
    ('sentry2', False, []), #["sentry1@jabbers.one", "sentry3@jabbers.one"]),
    ('sentry3', False, []), #["sentry2@jabbers.one", "sentry1@jabbers.one"]),
    ('sentry4', False, []),
    # ('sentry5', False, []),
    # ('sentry6', False, []),
    # ('sentry7', False, []),
    # ('sentry8', False, [])
]

if __name__ == '__main__':

    # initialize all agents
    for agent_name, agent_type in agent_names:
        agent = agent_type(agent_name+'@jabbers.one', 'aasd_erif')
        future = agent.start()
        future.result()  # wait for agent to initialize

    for sentryName, logging, neighbors in sentries:
        agent = SentryAgent(str(sentryName) + '@jabbers.one', "aasd_erif")
        agent.set("neighbors", neighbors)
        agent.set("logging", logging)
        agent.set("mySelf", str(sentryName))
        agent.start(auto_register=True)

        future.result()  # wait for agent to initialize
    time.sleep(2)  # wait long enough to initialize all agents
    print('All agents initialized. System ready to operate.')

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:  # stop program (stop button in PyCharm)
            quit_spade()  # terminate all agents and their processes
            break
    print("\nAgents terminated")
