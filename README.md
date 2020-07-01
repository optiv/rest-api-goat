# REST API Goat

This is a "Goat" project so you can get familiar with REST API testing. 
There is an included Postman project so you can see how everything is meant
to be called. If you encounter any components of the API which don't work
correctly, please create an Issue for them. 

## How To:
Make sure you can run `pipenv`. On Macs, this easily is installed once homebrew
is installed. Hit up Teams for how to install homebrew (or Google it).

1. `pipenv shell`
2. `pip install flask`
3. `export FLASK_APP=server.py`
4. `flask run`

If everything went ok, you should have the Goat running on localhost:5000. Try
to load the following URL in your brower and look for a basic "Hello" page:

http://localhost:5000/

## How To (Docker)

1. `docker build -t rest-api-goat:latest .`
2. `docker run -d -p 5000:5000 rest-api-goat`
3. Test at http://localhost:5000/

## Credentials
You have been given the following credentials:

| API Token            | Company Number |
|--------------------- | -------------: |
| vfuzd2nvaweojqolm4kq | 1              |
| ek9chlb4t96sncbr9dgx | 1              |
| x6oici7wh3prgx34fxo1 | 2              |
| 7eojwd75kqd80m4sm169 | 2              |
| jyrvm14k9tvdiesxwgku | 3              |

API tokens are typically provided as header values; see the Postman collection
for examples of how these tokens are used.

## API overview:
This API models a multi-tenant banking API. Banks have API tokens they use to
authenticate with the API. Banks should only be able to see information about
their own customers, and shouldn't be able to determine the balance of customers
of another bank.

The server-side code is written in Python (using Flask) and data persistence is
handled by SQLite. (You can think of this as a SQL server.) 

## API Methods:

### Basic Methods:
#### Authenticate
This is a basic method that checks if your token is good and tells you stuff
about your current user.

#### Get Customers
This method shows you all the customers of your bank and their balances

#### Get Customer v1
Used to get information about one specific customer. It was not implemented
correctly and a new developer was hired to fix its security problem.

#### Get Customer v2
This is the new version that the new developer claims fixes the issue from
v1 and is now secure. Is it?

#### Create Access Token
Creates a new access token tied to the current user's company. A bank might use
this to give each API client they own a unique ID. 

#### Delete Token
Deletes an access token. (Known bug: you can delete all of a company's access
tokens. If you do this and can't get back in, run `python install_db.py` to reset
everthing.)

### Transfers:
All transfers are a 3-step process. First, a transfer is created. It contains
information about who is sending money, who is receiving it, and how much.

Next, the banks wanted a way to batch all the transfers together. They thought
this would be better than processing each one individually. Decisions about
whether or not the transfer is valid are made here.

Finally, transfers are completed individually. Why banks wanted this instead of
batching the entire transaction together is not explained in any documentation.

#### Create Transfer
The money sender, money receiver, and ammount are submitted. The server will
accept anything for which the JSON is valid and possesses the required information.
Don't expect error checking at this step.

#### Process Transfers
Takes all transfers in the "CREATED" state and determines if they should be
submitted or not. Returns a list of ID values which were accepted ("pending")
and which ones were rejected ("failed"). Customer balances are not changed.

#### Confirm Transfer
Takes an ID value and completes the transfer if it's in the PENDING state. This
step changes customer balances and transfers the money.

#### Get Tranfers
Shows a list of all transfers in the system and their state. API clients can
also filter on state, such as "CREATED", "PENDING", or "COMPLETE".

## What to Test for:
The answer to this question always starts with "What is this API's threat model?"
If you're Billy Badguy, what kind of things would you want to do? Billy Badguy
doesn't want to live in his friend's basement anymore, but he doesn't want a job
either. How's he going to get rent money?

See the "Guide" folder of this project for clues and hints. See what you can figure
out without help first!
