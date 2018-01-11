import numpy as np


class Obligation:
    __slots__ = ['amount', 'from_', 'to', 'timeToOpen', 'timeToPay', 'timeToReceive', 'simulation', 'fulfilled']

    def __init__(self, contract, amount: np.longdouble, timeLeftToPay: int) -> None:
        self.amount = np.longdouble(amount)

        self.from_ = contract.getLiabilityParty()
        self.to = contract.getAssetParty()

        # there is only one simulation shared by all agents
        self.simulation = self.from_.getSimulation()
        self.timeToOpen = self.simulation.getTime() + 1
        self.timeToPay = self.simulation.getTime() + timeLeftToPay
        self.timeToReceive = self.timeToPay + 1

        assert self.timeToPay >= self.timeToOpen

        self.fulfilled = False

    def fulfil(self):
        pass

    def getAmount(self) -> np.longdouble:
        return self.amount

    def isFulfilled(self) -> bool:
        return self.fulfilled

    def hasArrived(self) -> bool:
        return self.simulation.getTime() == self.timeToOpen

    def isDue(self) -> bool:
        return self.simulation.getTime() == self.timeToPay

    def getFrom(self):
        return self.from_

    def getTo(self):
        return self.to

    def setFulfilled(self) -> None:
        self.fulfilled = True

    def setAmount(self, amount) -> None:
        self.amount = amount

    def getTimeToPay(self) -> int:
        return self.timeToPay

    def getTimeToReceive(self) -> int:
        return self.timeToReceive

    def printObligation(self) -> None:
        print("Obligation from ", self.getFrom().getName(), " to pay ",
              self.getTo().getName(), " an amount ", self.getAmount(),
              " on timestep ", self.getTimeToPay(), " to arrive by timestep ",
              self.getTimeToReceive())


class ObligationMessage:
    def __init__(self, sender, message) -> None:
        self.sender = sender
        self.message = message
        self._is_read = False

    def getSender(self):
        return self.sender

    def getMessage(self):
        self._is_read = True
        return self.message

    def is_read(self) -> bool:
        return self._is_read


class ObligationsAndGoodsMailbox:
    def __init__(self, me) -> None:
        self.me = me
        self.obligation_unopened = []
        self.obligation_outbox = []
        self.obligation_inbox = []
        self.obligationMessage_unopened = []
        self.obligationMessage_inbox = []
        self.goods_inbox = []

    def receiveObligation(self, obligation) -> None:
        self.obligation_unopened.append(obligation)

        print("Obligation sent. ", obligation.getFrom().getName(),
              " must pay ", obligation.getAmount(), " to ",
              obligation.getTo().getName(),
              " on timestep ", obligation.getTimeToPay())

    def receiveMessage(self, msg) -> None:
        self.obligationMessage_unopened.append(msg)
        # print("ObligationMessage sent. " + msg.getSender().getName() +
        #        " message: " + msg.getMessage());

    def receiveGoodMessage(self, good_message) -> None:
        print(good_message)
        self.goods_inbox.append(good_message)
        # print("ObligationMessage sent. " + msg.getSender().getName() +
        #        " message: " + msg.getMessage());

    def addToObligationOutbox(self, obligation) -> None:
        self.obligation_outbox.append(obligation)

    def getMaturedObligations(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_inbox if o.isDue() and not o.isFulfilled()])

    def getAllPendingObligations(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_inbox if not o.isFulfilled()])

    def getPendingPaymentsToMe(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_outbox if o.isFulfilled()])

    def fulfilAllRequests(self) -> None:
        for o in self.obligation_inbox:
            if not o.isFulfilled():
                o.fulfil()

    def fulfilMaturedRequests(self) -> None:
        for o in self.obligation_inbox:
            if o.isDue() and not o.isFulfilled():
                o.fulfil()

    def step(self) -> None:
        # Process goods_inbox
        for good_message in self.goods_inbox:
            self.me.getMainLedger().create(good_message.good_name, good_message.amount, good_message.value)
        self.goods_inbox.clear()

        # Remove all fulfilled requests
        self.obligation_inbox = [o for o in self.obligation_inbox if not o.isFulfilled()]
        self.obligation_outbox = [o for o in self.obligation_outbox if not o.isFulfilled()]

        # Remove all requests from agents who have defaulted.
        # TODO should be in model not in the library
        self.obligation_outbox = [o for o in self.obligation_outbox if o.getFrom().isAlive()]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.obligation_inbox += [o for o in self.obligation_unopened if o.hasArrived()]
        self.obligation_unopened = [o for o in self.obligation_unopened if not o.hasArrived()]

        # Remove all fulfilled requests
        self.obligationMessage_inbox = [o for o in self.obligationMessage_inbox if not o.is_read()]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.obligationMessage_inbox += list(self.obligationMessage_unopened)
        self.obligationMessage_unopened = []

        # Remove all fulfilled requests
        assert not self.goods_inbox

        # Move all messages in the obligation_unopened to the obligation_inbox

    def printMailbox(self) -> None:
        if ((not self.obligation_unopened) and (not self.obligation_inbox) and
           (not self.obligation_outbox)):
            print("\nObligationsAndGoodsMailbox is empty.")
        else:
            print("\nObligationsAndGoodsMailbox contents:")
            if not (not self.obligation_unopened):
                print("Unopened messages:")
            for o in self.obligation_unopened:
                o.printObligation()

            if not (not self.obligation_inbox):
                print("Inbox:")
            for o in self.obligation_inbox:
                o.printObligation()

            if not (not self.obligation_outbox):
                print("Outbox:")
            for o in self.obligation_outbox:
                o.printObligation()
            print()

    def getMessageInbox(self):
        return self.obligationMessage_inbox

    def getObligation_outbox(self):
        return self.obligation_outbox

    def getObligation_inbox(self):
        return self.obligation_inbox
