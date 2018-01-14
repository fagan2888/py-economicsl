import numpy as np


class Obligation:
    __slots__ = ['amount', 'from_', 'to', 'time_to_open', 'time_to_pay', 'time_to_receive', 'simulation', 'fulfilled']

    def __init__(self, contract, amount: np.longdouble, timeLeftToPay: int) -> None:
        self.amount = np.longdouble(amount)

        self.from_ = contract.get_liability_party()
        self.to = contract.get_asset_party()

        # there is only one simulation shared by all agents
        self.simulation = self.from_.get_simulation()
        self.time_to_open = self.simulation.get_time() + 1
        self.time_to_pay = self.simulation.get_time() + timeLeftToPay
        self.time_to_receive = self.time_to_pay + 1

        assert self.time_to_pay >= self.time_to_open

        self.fulfilled = False

    def fulfil(self):
        pass

    def get_amount(self) -> np.longdouble:
        return self.amount

    def is_fulfilled(self) -> bool:
        return self.fulfilled

    def has_arrived(self) -> bool:
        return self.simulation.get_time() == self.time_to_open

    def is_due(self) -> bool:
        return self.simulation.get_time() == self.time_to_pay

    def get_from(self):
        return self.from_

    def get_to(self):
        return self.to

    def set_fulfilled(self) -> None:
        self.fulfilled = True

    def set_amount(self, amount) -> None:
        self.amount = amount

    def get_time_to_pay(self) -> int:
        return self.time_to_pay

    def get_time_to_receive(self) -> int:
        return self.time_to_receive

    def print_obligation(self) -> None:
        print("Obligation from ", self.get_from().get_name(), " to pay ",
              self.get_to().get_name(), " an amount ", self.get_amount(),
              " on timestep ", self.get_time_to_pay(), " to arrive by timestep ",
              self.get_time_to_receive())


class Mailbox:
    def __init__(self, me) -> None:
        self.me = me
        self.obligation_unopened = []
        self.obligation_outbox = []
        self.inbox = {'obligation': [], 'goods': []}

    def receive_message(self, message) -> None:
        if isinstance(message, Obligation):
            self.obligation_unopened.append(message)

            print("Obligation sent. ", message.get_from().get_name(),
                  " must pay ", message.get_amount(), " to ",
                  message.get_to().get_name(),
                  " on timestep ", message.get_time_to_pay())
        else:
            print(good_message)
            self.inbox['goods'].append(good_message)

    def add_to_obligation_outbox(self, obligation) -> None:
        self.obligation_outbox.append(obligation)

    def get_matured_obligations(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.inbox["obligation"] if o.is_due() and
                    not o.is_fulfilled()])

    def get_all_pending_obligations(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.inbox["obligation"] if not o.is_fulfilled()])

    def get_pending_payments_to_me(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.obligation_outbox if o.is_fulfilled()])

    def fulfil_all_requests(self) -> None:
        for o in self.inbox["obligation"]:
            if not o.is_fulfilled():
                o.fulfil()

    def fulfil_matured_requests(self) -> None:
        for o in self.inbox["obligation"]:
            if o.is_due() and not o.is_fulfilled():
                o.fulfil()

    def step(self) -> None:
        # Process inbox["goods"]
        for good_message in self.inbox["goods"]:
            self.me.get_main_ledger().create(good_message.good_name, good_message.amount, good_message.value)
        self.inbox['goods'].clear()

        # Remove all fulfilled requests
        self.inbox["obligation"] = [o for o in self.inbox["obligation"] if not o.is_fulfilled()]
        self.obligation_outbox = [o for o in self.obligation_outbox if not o.is_fulfilled()]

        # Remove all requests from agents who have defaulted.
        # TODO should be in model not in the library
        self.obligation_outbox = [o for o in self.obligation_outbox if o.get_from().is_alive()]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.inbox["obligation"] += [o for o in self.obligation_unopened if o.has_arrived()]
        self.obligation_unopened = [o for o in self.obligation_unopened if not o.has_arrived()]

        # Remove all fulfilled requests
        assert not self.inbox['goods']

        # Move all messages in the obligation_unopened to the obligation_inbox

    def print_mailbox(self) -> None:
        if ((not self.obligation_unopened) and (not self.inbox["obligation"]) and
           (not self.obligation_outbox)):
            print("\nObligationsAndGoodsMailbox is empty.")
        else:
            print("\nObligationsAndGoodsMailbox contents:")
            if not (not self.obligation_unopened):
                print("Unopened messages:")
            for o in self.obligation_unopened:
                o.print_obligation()

            if not (not self.inbox["obligation"]):
                print("Inbox:")
            for o in self.inbox["obligation"]:
                o.print_obligation()

            if not (not self.obligation_outbox):
                print("Outbox:")
            for o in self.obligation_outbox:
                o.print_obligation()
            print()

    def get_obligation_outbox(self):
        return self.obligation_outbox

    def get_obligation_inbox(self):
        return self.inbox["obligation"]
