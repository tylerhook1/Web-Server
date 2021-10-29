from flask import Flask, request
import json
app = Flask(__name__)

# creates an empty list for incoming transactions and
# an empty dictionary to keep track of current point balances
transactions = []
balances = {}

@app.route('/')
def index():
    return '<h1>It Worked!</h1>'

# a route to take in transactions
@app.route('/transaction', methods=['POST'])
def transaction():
    global transactions
    global balances
    # receives the transaction request and assigns it to
    # trans_data, adds trans_data to the transactions list,
    # and sorts the new list by timestamp.
    trans_data = request.get_json()
    transactions.append(trans_data)
    transactions = sorted(transactions,key=lambda  i: i['timestamp'])

    # Adds the new transaction and updates the points to the
    # current balances. If the payer is new, it adds the payer
    # to the balances and includes the points.
    if trans_data['payer'] in balances:
        balances[trans_data['payer']] += trans_data['points']
    else:
        balances[trans_data['payer']] = trans_data['points']

    return "<h1>Payment added.</h1>"

# a route to handle points to be spent
@app.route('/spend_points', methods=['POST'])
def spend_points():
    global transactions
    global balances
    # assings the points to be spent to a variable
    # and creates a list to hold the payers and points
    # that are used
    points = request.get_json()['points']
    points_taken = []

    # loops through the transaction list to use points
    # from the oldest transactions in the list
    while points > 0:
        # Finds whether the oldest transaction payer is already in
        # points_taken and returns the index if it is there.
        ind = next((i for i,d in enumerate(points_taken) if transactions[0]['payer'] in d),None)

        # checks to see whether the points to be spent are
        # greater or less than the points in the oldest transaction
        if transactions[0]['points'] >= points:
            # if the points to be spent are less than or equal to the points
            # in the oldest transaction, we remove the points to be spent from
            # the tranasaction and update the balance for that payer
            transactions[0]['points'] -= points
            balances[transactions[0]['payer']] -= points

            # if the payer is currently in points_taken then it adds the points
            # to the payer in the list, if not it adds the new payer and the
            # points to the list
            if ind == None:
                new_trans = {transactions[0]['payer']:-points}
                points_taken.append(new_trans)
            else:
                points_taken[ind][transactions[0]['payer']] -= points

            # if the remaining points in the oldest transaction is 0 then we
            # remove that transaction from the list
            if transactions[0]['points'] == 0:
                transactions.pop(0);

            # return the list of payers and points that were spent
            return json.dumps(points_taken)

        else:
            # if the points to be spent are greater than the points in the oldest
            # transaction we subtract the transaction points from the remaining
            # points to be spent and updates the balance for that payer
            points -= transactions[0]['points']
            balances[transactions[0]['payer']] -= transactions[0]['points']

            # if the payer is currently in points_taken then it adds the points
            # to the payer in the list, if not it adds the new payer and the
            # points to the list
            if ind == None:
                new_trans = {transactions[0]['payer']:-transactions[0]['points']}
                points_taken.append(new_trans)
            else:
                points_taken[ind][transactions[0]['payer']] -= transactions[0]['points']

            # removes the now empty transaction from the dict_list
            transactions.pop(0);

#route to return the point balances for payers
@app.route('/point_balance', methods=['GET'])
def point_balance():
    global balances
    return balances

if __name__ == '__main__':
    app.run()
