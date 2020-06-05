# Guide

This guide is meant as a learning tool for when you get stuck. Try to
figure out the objectives yourself first, before looking for hints in
this guide. The clues are meant to give progressively more guidance
to help you find the solution. This guide is *not* meant to give you
the solution itself. If you find yourself still stuck after giving it
several attempts, try to reach out for help in the Teams chat. You
don't have to tell everyone that you're doing a Goat; pretend it's
for a client

**Note:** When doing an assessment, you aren't going to have a list
of objectives/known issues to hunt for. See how many weaknesses you
can find on your own first!

## Blackbox Testing

#### Get Customer v1
<details>
  <summary>Objective 1</summary>
  Clue: What happens when you change the number at the end of this URL?
</details>

#### Get Customer v2
<details>
  <summary>Objective 1</summary>
  Clue: What happens when you change the number at the end of this URL to a string?
</details>

#### Create Transfer
<details>
  <summary>Objective 1</summary>
  Clue: Send $50 from one user to another. Now send $50 back, but don't change `to` and `from`
</details>

#### Get Transfers (All)
<details>
  <summary>Objective 1</summary>
  No known issues with this endpoint, but if you find one let me know!
</details>

#### Get Transfers (Created)
<details>
  <summary>Objective 1</summary>
  No known issues with this endpoint, but if you find one let me know!
</details>

#### Authenticate
<details>
  <summary>Objective 1</summary>
  This is a complex objective. Analyze the application's source code and determine how `Create Access Token` works.
  If there were a large number of access tokens present in the system, could you determine which ones are real?
</details>

### Transfers
This use may use `Create Transfer`, `Process Transfer`, `Confirm Transfer`, or a combination:
<details>
  <summary>Objective 1</summary>
  Clue: Use "Create Transfer" to make a transfer request for $100,000. What happens when you process
  this request? Can you bypass this constraint?
</details>

<details>
  <summary>Objective 2</summary>
  Clue: Objective 1 can be completed in at least two ways. If you used the solution to "Create Transfer"
  Objective 1, can you solve it some other way? What happens if Robert needs to make two transfers to Juan?
</details>


### No Known Issues:
The following API methods do not have known issues. If you find one, please let me know!
* Get Customers

### Others
I haven't offered clues for all methods on purpose. Some offer a second change to practice one of the
weaknesses above. See if you can find problems with them. (I'm also moving pretty fast and might have
just forgotten some of them. Sorry!)

## Source Code
Common source code assessment goals:
* How does routing work? Can you identify any endpoints which aren't referenced in the Postman collect?
* What are common strings to grep for?
	- Do any "TODO" comments shed light on known issues?
	- The API uses a SQL backend. Is SQL Injection possible? How would you find it in code?
	- Cross-Site Scripting might not apply to this application.
* Can you spot any logic errors in the Transfer workflow? Has breaking it into 3 steps exposed it to any weaknesses?
* Can you predict API tokens? (Note: The initial 5 tokens may not fit the pattern.)