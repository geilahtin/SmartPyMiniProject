import smartpy as sp

class Lottery (sp.Contract):
    def __init__(self):
        #storage
        self.init(
            players= sp.map(l= {}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost= sp.tez(1),
            tickets_available= sp.nat(5),
            max_tickets= sp.nat(5),
            operator = sp.test_account("admin").address
        )
    @sp.entry_point
    def buy_ticket(self,no_of_tickets):
        sp.set_type(no_of_tickets, sp.TNat)

        #create a local value for for_loop
        x = sp.local("x", 0)
    
        #assertions
        sp.verify(self.data.tickets_available>0, "NO TICKETS AVAILABLE")
        sp.verify(sp.amount >= sp.mul(self.data.ticket_cost,no_of_tickets), "INVALID AMOUNT")

        y = sp.local('y', no_of_tickets)

        #check if available tickets are not greater than the tickets to be bought
        sp.if sp.to_int(no_of_tickets) > sp.to_int(self.data.tickets_available):
            y.value = self.data.tickets_available
        sp.else:
            y.value = no_of_tickets
        
        #storage changes
        sp.while x.value < y.value:
            self.data.players[sp.len(self.data.players)] = sp.sender
            x.value = x.value + 1
            
        #update number of available tickets
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - y.value)

        #return extra tez
        extra_amount= sp.amount- sp.mul(self.data.ticket_cost,y.value)
        sp.if extra_amount > sp.tez(0):
            sp.send(sp.sender, extra_amount)

    @sp.entry_point
    def end_game(self, random_number):
        sp.set_type(random_number, sp.TNat)
        
        #assertion
        sp.verify(self.data.tickets_available == 0, "GAME IS STILL ON")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")
        
        #generate winning index
        winner_index = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]

        #send reward to winner
        sp.send(winner_address, sp.balance)

        #reset the game
        self.data.players= {}
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def change_ticket_cost(self, ticket_cost):
        sp.set_type(ticket_cost, sp.TMutez)
        
        #assertion
        sp.verify(self.data.tickets_available == 0, "GAME IS STILL ON")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")
        sp.verify(ticket_cost >= sp.tez(1), "INVALID AMOUNT")

        #change ticket cost 
        self.data.ticket_cost = ticket_cost

    @sp.entry_point
    def change_max_no_tickets(self, max_tickets):
        sp.set_type(max_tickets, sp.TNat)
        
        #assertion
        sp.verify(self.data.tickets_available == 0, "GAME IS STILL ON")
        sp.verify(sp.sender == self.data.operator, "NOT AUTHORISED")
        sp.verify(max_tickets >= sp.nat(1), "INVALID AMOUNT")

        #change max number of tickets
        self.data.max_tickets = max_tickets
        

@sp.add_test(name="main")
def test():
    scenario = sp.test_scenario()

    #Test accounts
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    john = sp.test_account("john")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")

    #contract instance
    lottery=Lottery()
    scenario += lottery
    
    #buy_ticket
    scenario += lottery.buy_ticket(6).run(
        amount= sp.tez(6), sender=alice
    ) 
    #scenario += lottery.buy_ticket(3).run(
    #    amount= sp.tez(5), sender=bob
    #)


    #change max tickets
    scenario+= lottery.change_max_no_tickets(10).run(sender=admin)

    #change ticket cost
    scenario+= lottery.change_ticket_cost(sp.tez(2)).run(sender=admin)
    
    #end_game
    scenario += lottery.end_game(21).run(now= sp.timestamp(3), sender= admin)
        
