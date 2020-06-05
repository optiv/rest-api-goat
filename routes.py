import json
import server

def row2dict(row):
	"""Takes sqlite3.Row objects and converts them to dictionaries.
	This is important for JSON serialization because otherwise
	Python has no idea how to turn a sqlite3.Row into JSON."""
	x = {}
	for col in row.keys():
		x[col] = row[col]
	return x

def check_token(api_token):
	# TODO: try some fancy JOIN for user + company
	c = server.get_db().cursor()
	c.execute("SELECT * FROM tokens WHERE api_token=? LIMIT 1", [api_token])
	user = c.fetchone()
	if user is not None:
		response = {"success": True}
		response["user"] = row2dict(user)
		c.execute("SELECT * FROM companies WHERE id=? LIMIT 1", [user["company"]])
		company = c.fetchone()
		response["company"]  = {"name": company["name"], "id": company["id"]}
	else:
		response = {"success": False, "error": "Invalid API token."}
	return response

@server.app.route('/authenticate', methods=['POST'])
def authenticate():
	content = server.request.json
	try:
		api_token = content["api_token"]
		response = check_token(api_token)
		return response
	except KeyError:
		response = {"success": False, "error": "No API token given."}
		return response

@server.app.route('/get_customers')
def get_customers():
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	c = server.get_db().cursor()
	c.execute("SELECT * FROM customers WHERE company=?", [auth["company"]["id"]])
	rows = c.fetchall()
	response = {
		"success": True,
		"customers": []
	}

	for row in rows:
		x = row2dict(row)
		response["customers"].append(x)
	return response

# goatnote:
# SQLi
@server.app.route('/get_customer_v2/<id>')
def get_customer2(id):
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	c = server.get_db().cursor()
	c.execute("SELECT * FROM customers WHERE company=" + str(auth["company"]["id"]) + " AND id=" + id)
	rows = c.fetchall()
	response = {
		"success": True,
		"customers": []
	}

	for row in rows:
		x = {}
		for col in row.keys():
			x[col] = row[col]
		response["customers"].append(x)
	return response

# goatnote:
# IDOR
@server.app.route('/get_customer_v1/<id>')
def get_customer1(id):
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	c = server.get_db().cursor()
	c.execute("SELECT * FROM customers WHERE id=?", [id])
	rows = c.fetchall()
	response = {
		"success": True,
		"customers": []
	}

	for row in rows:
		x = {}
		for col in row.keys():
			x[col] = row[col]
		response["customers"].append(x)
	return response

@server.app.route('/transfer', methods=['PUT'])
def create_transfer():
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	content = server.request.json
	if content is None:
		response = {"success": False, "error": "Expected JSON content"}
		return response
	try:
		cust_from = int(content["from"])
		cust_to = int(content["to"])
		ammount = content["ammount"]
	except KeyError:
		response = {"success": False, "error": "Missing 'from', 'to', or 'ammount'"}
		return response
	except ValueError:
		response = {"success": False, "error": "Values of 'from' and 'to' should be customer IDs."}
		return response

	# Decimals maintain more accuracy than floats (or should) so we don't want
	# this number as a float. However, all decimals should be valid floats.
	# TODO: Python has a decimal type, should probably use that?
	try:
		float(ammount)
	except ValueError:
		response = {"success": False, "error": "Value of 'ammount' should be a decimal number"}
		return response

	# goatnote:
	# Not doing: validation of cust_from or cust_to
	db = server.get_db()
	c = db.cursor()
	try:
		c.execute('INSERT INTO transfers VALUES (null, ?, ?, ?, ?)', [cust_from, cust_to, ammount, 'CREATED'])
		db.commit()
	except:
		response = {"success": False, "error": "Unknown SQL error"}
		raise
		return response

	response = {"success": True, "id": c.lastrowid}
	return response


@server.app.route('/get_transfers')
@server.app.route('/get_transfers/<status>')
def get_transfers(status=None):
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	c = server.get_db().cursor()
	if status is None:
		c.execute("SELECT * FROM transfers")
	else:
		c.execute("SELECT * FROM transfers WHERE status=?", [status])
	rows = c.fetchall()
	response = {
		"success": True,
		"transfers": [],
		"where": status
	}

	for row in rows:
		x = {}
		for col in row.keys():
			x[col] = row[col]
		response["transfers"].append(x)
	return response

@server.app.route('/process_transfers/', methods=['POST'])
def process_transfers():
	"""Advances all CREATED transfers to pending if they look ok.
	Will not complete the transfer; use /confirm-transfer/<id> for that."""

	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	db = server.get_db()
	c = db.cursor()
	transfers = c.execute("SELECT * FROM transfers WHERE status=?", ['CREATED']).fetchall()
	#x = []
	#for row in transfers:
	#	x.append(row2dict(row))
	#return {"data": x}
	
	ok = []
	error = []
	# goatnote:
	# Logic error here allows balances to become overdrawn
	for xfer in transfers:
		balance = c.execute("SELECT balance from customers WHERE id=?", [xfer["custID_from"]]).fetchone()
		if balance["balance"] > xfer["amount"]:
			c.execute("UPDATE transfers SET status=? WHERE id=?", ['PENDING', xfer['id']])
			ok.append(xfer['id'])
		else:
			error.append(xfer['id'])
	response = {"success": True, "pending": ok, "failed": error}

	db.commit()
	return response

# What even is database optimization?
@server.app.route('/confirm_transfer/<xfer_id>', methods=['POST'])
def confirm_transfer(xfer_id):

	db = server.get_db()
	c = db.cursor()

	try:
		xfer_id = int(xfer_id)
	except ValueError:
		response = {"success": False, "error": "Transfer ID must be an integer"}
		return response
	
	xfer = c.execute("SELECT * FROM transfers WHERE id=? LIMIT 1", [xfer_id]).fetchone()
	if xfer is None:
		response = {"success": False, "error": "Transfer ID invalid"}
		return response

	c.execute("UPDATE transfers SET status=? WHERE id=? AND status=?", ['COMPLETE', xfer['id'], 'PENDING'])
	if c.rowcount == 0:
		response = {"success": False, "error": "Transfer ID {} was not in the 'PENDING' state".format(xfer_id)}
		return response
	else:
		customer_to = c.execute("SELECT * from customers WHERE id=?", [xfer['custID_to']]).fetchone()
		customer_from = c.execute("SELECT * from customers WHERE id=?", [xfer['custID_from']]).fetchone()

		new_balance_from = customer_from['balance'] - xfer['amount']
		c.execute('UPDATE customers SET balance=? WHERE id=?', [new_balance_from, xfer['custID_from']])

		new_balance_to = customer_to['balance'] + xfer['amount']
		c.execute('UPDATE customers SET balance=? WHERE id=?', [new_balance_to, xfer['custID_to']])

		response = {"success": True}

		db.commit()
		return response

@server.app.route('/token/<token>', methods=['DELETE'])
def delete_token(token):
	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	db = server.get_db()
	c = db.cursor()

	# Crazy logic to say "Delete only if there's at least 1 more token for this company."
	c.execute('DELETE FROM tokens WHERE api_token=?', [token])

	db.commit()
	if c.rowcount > 0:
		result = {"success": True}
	else:
		result = {"success": False, "error": "No such token"}
	return result


@server.app.route('/new_token', methods=["POST", "PUT"])
def assign_new_token():
	"""Builds a new API token and assigns it to the current user's
	company. If a bank wanted each client to use a unique token,
	perhaps so that they can identify which API client from logged
	data, they might use this method.

	If you think this method looks too sloppy to be real code,
	you don't do enough source code assessments."""

	from hashlib import sha256

	api_token = server.request.headers.get('X-API-Token')
	auth = check_token(api_token)
	if not auth["success"]:
		return auth

	db = server.get_db()
	c = db.cursor()

	# TODO: SHA256 is secure, but is there a better way to do this?
	row = c.execute('SELECT MAX(id) FROM tokens').fetchone()
	old_token_id = row[0]

	# Hashing methods only take bytes objects.
	# All this says is "give me '5' as a byte array"
	num = bytes(str(old_token_id), 'utf-8')
	h = sha256()
	h.update(num)
	out = h.digest()

	# We don't want bytes, we want 20-character strings using 0-9 and a-z
	# This causes some truncation and loss of entropy
	# TODO: longer tokens to maintain entropy?
	out = out[:20]
	out_modulo = [int(x) % 36 for x in out] # 36 = 26 letters + 10 digits

	for i in range(len(out_modulo)):
		if out_modulo[i] < 10:
			out_modulo[i] = str(out_modulo[i])
		else:
			out_modulo[i] = chr(ord('a') + out_modulo[i] - 10)
	
	new_token = ''.join(out_modulo)

	c.execute('INSERT INTO tokens VALUES (null, ?, ?)', [new_token, auth["user"]["company"]])
	db.commit()

	result = {
		"success": True,
		"id": c.lastrowid,
		"token": new_token
	}

	return result


@server.app.route('/get_company/<comp_id>')
def get_company(comp_id):
	c = server.get_db().cursor()
	company = c.execute("SELECT * FROM companies WHERE id=?", [comp_id]).fetchone()

	if company is not None:
		result = {"success": True, "data": row2dict(company)}
		return result
	else:
		result = {"success": False, "error": "Company ID {} not found".format(comp_id)}
		return result
