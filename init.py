#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import datetime
import random

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='127.0.0.1',
                       user='root',
                       password='root',
                       database='airline_ticket', #修改名字
					   port=3306,
					   charset='utf8mb4')

@app.route('/')
def hello():
    error = request.args.get('error')
    return render_template('index.html',error=error)

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    usrtype = request.form['usrtype']

	# cursor used to send queries
    cursor = conn.cursor()

    if usrtype == 'customer':
        query = 'SELECT * FROM customer WHERE email = \'{}\' and password = md5(\'{}\')'
    elif usrtype == 'agent':
        query = 'SELECT * FROM booking_agent WHERE email = \'{}\' and password = md5(\'{}\')'
    else:
        query = 'SELECT * FROM airline_staff WHERE username = \'{}\' and password = md5(\'{}\')'

    cursor.execute(query.format(username, password))
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        session['username'] = username
        if usrtype == 'staff':
            return redirect(url_for('staffHome'))
        elif usrtype == 'customer':
            return redirect(url_for('homeCustomer'))
        else:
            return redirect(url_for('homeAgent'))
    else:
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Define route for customer register
@app.route('/registerCustomer')
def registerCustomer():
	return render_template('registerCustomer.html')

#Authenticates the register for customer
@app.route('/registerAuthCustomer', methods=['GET', 'POST'])
def registerAuthCustomer():
	#grabs information from the forms
	email = request.form['email']
	name = request.form['name']
	password = request.form['password']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = request.form['phone_number']
	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM customer WHERE email = \'{}\'"
	cursor.execute(query.format(name))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('registerCustomer.html', error = error)
	else:
		ins = "INSERT INTO customer VALUES(\'{}\', \'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
		cursor.execute(ins.format(email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
		conn.commit()
		cursor.close()
		flash("You are logged in")
		return render_template('index.html')

#Define route for booking agent register
@app.route('/registerAgent')
def registerAgent():
	return render_template('registerAgent.html')

#Authenticates the register for agent
@app.route('/registerAuthAgent', methods=['GET', 'POST'])
def registerAuthAgent():
	#grabs information from the forms
	email = request.form['username']
	password = request.form['password']
	booking_agent_id = request.form['booking_agent_id']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM booking_agent WHERE email = \'{}\'"
	cursor.execute(query.format(email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('registerAgent.html', error = error)
	else:
		ins = "INSERT INTO booking_agent VALUES(\'{}\', md5(\'{}\'), \'{}\')"
		cursor.execute(ins.format(email, password, booking_agent_id))
		conn.commit()
		cursor.close()
		flash("You are logged in")
		return render_template('index.html')

#Define route for staff register
@app.route('/registerStaff')
def registerStaff():
	return render_template('registerStaff.html')

#Authenticates the register for staff
@app.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline_name = request.form['airline_name']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM airline_staff WHERE username = \'{}\'"
	cursor.execute(query.format(username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('registerStaff.html', error = error)
	else:
		ins = "INSERT INTO airline_staff VALUES(\'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\', \'{}\')"
		cursor.execute(ins.format(username, password, first_name, last_name, date_of_birth, airline_name))
		conn.commit()
		cursor.close()
		flash("You are logged in")
		return render_template('index.html')

#------------------------------------------------------------------------------------------------------------
@app.route('/homeCustomer')
def homeCustomer():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
				AND customer_email = \'{}\' AND departure_time > curdate()'
    cursor.execute(query.format(username))
    data = cursor.fetchall() 
    cursor.close()
    message = request.args.get('message')
    return render_template('homeCustomer.html', username=username, posts=data, message=message)

@app.route('/homeCustomer/viewFlightCustomer', methods=['POST'])
def viewFlightCustomer():
    username = session['username']
    cursor = conn.cursor()
    fromdate = request.form['fromdate']
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    todate = request.form['todate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']
    print(username, fromdate, todate, fromcity, fromairport, tocity, toairport)
    # Get flight information in the given period
    query = 'SELECT purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight, airport \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
                AND flight.departure_airport = airport.airport_name \
				AND purchases.customer_email = %s \
                AND flight.departure_time BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) \
                AND airport.airport_city = %s AND airport.airport_name = %s \
                AND (flight.airline_name, flight.flight_num) in \
                    (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                    WHERE airport.airport_name=flight.arrival_airport \
                    AND airport.airport_city = %s \
                    AND airport.airport_name = %s)'

    cursor.execute(query, (username, fromdate, todate, fromcity, fromairport, tocity, toairport))
    data = cursor.fetchall() 
    cursor.close()
    if (data):
        return render_template('viewFlightCustomer.html', username=username, fromdate=fromdate, todate=todate, posts=data)
    else:
        error = 'No results found'
        return render_template('viewFlightCustomer.html', username=username, fromdate=fromdate, todate=todate, error=error) 

# Customer purchases
@app.route("/homeCustomer/purchasePageCustomer")
def purchasePageCustomer():
    return render_template('purchaseCustomer.html')

@app.route('/homeCustomer/searchPurchaseCustomer', methods=['POST'])
def searchPurchaseCustomer():
    cursor = conn.cursor()
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    fromdate = request.form['fromdate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']
    todate = request.form['todate']
    query = 'SELECT * FROM flight, airport \
            WHERE airport.airport_name = flight.departure_airport \
            AND airport.airport_city = %s \
            AND airport.airport_name = %s \
            AND flight.status = "Upcoming"\
            AND %s BETWEEN DATE_SUB(flight.departure_time, INTERVAL 2 DAY) AND DATE_ADD(flight.departure_time, INTERVAL 2 DAY) \
            AND %s BETWEEN DATE_SUB(flight.arrival_time, INTERVAL 2 DAY) AND DATE_ADD(flight.arrival_time, INTERVAL 2 DAY) \
            AND (flight.airline_name, flight.flight_num) in \
                (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                WHERE airport.airport_name=flight.arrival_airport \
                AND airport.airport_city = %s \
                AND airport.airport_name = %s)'
    cursor.execute(query, (fromcity, fromairport, fromdate, todate, tocity, toairport))

    data = cursor.fetchall()
    cursor.close()
    error = None
    if (data):
        return render_template('purchaseCustomer.html', results=data)
    else:
        error = 'No results found'
        return render_template('purchaseCustomer.html', searchError=error) 

@app.route('/homeCustomer/purchaseCustomer', methods=['POST'])
def purchaseCustomer():
    cursor = conn.cursor()
    username = session['username']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    # generate ticket id
    queryCount = 'SELECT COUNT(*) as count FROM ticket'
    cursor.execute(queryCount)
    ticketCount = cursor.fetchone()
    ticket_id = ticketCount[0] + 1
    # Create the new ticket
    queryNewTicket = 'INSERT INTO ticket VALUES(%s, %s, %s)'
    cursor.execute(queryNewTicket, (ticket_id, airline_name, flight_num))
    # Finalize the purchase
    queryPurchase = 'INSERT INTO purchases VALUES(%s, %s, %s, CURDATE())'
    cursor.execute(queryPurchase, (ticket_id, username, None))
    conn.commit()
    cursor.close()
    return redirect(url_for('homeCustomer', message = 'Successfully Purchased a Ticket!'))

# Customer searches
@app.route('/homeCustomer/searchPageCustomer')
def searchPageCustomer():
  return render_template('searchCustomer.html')

@app.route('/homeCustomer/searchCustomer', methods=['POST'])
def searchCustomer():
    cursor = conn.cursor()
    username = session['username']
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    fromdate = request.form['fromdate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']
    todate = request.form['todate']
    query = 'SELECT * FROM flight, airport \
            WHERE airport.airport_name = flight.departure_airport \
            AND airport.airport_city = %s \
            AND airport.airport_name = %s \
            AND flight.status = "Upcoming"\
            AND %s BETWEEN DATE_SUB(flight.departure_time, INTERVAL 2 DAY) AND DATE_ADD(flight.departure_time, INTERVAL 2 DAY) \
            AND %s BETWEEN DATE_SUB(flight.arrival_time, INTERVAL 2 DAY) AND DATE_ADD(flight.arrival_time, INTERVAL 2 DAY) \
            AND (flight.airline_name, flight.flight_num) in \
                (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                WHERE airport.airport_name=flight.arrival_airport \
                AND airport.airport_city = %s \
                AND airport.airport_name = %s)'
    cursor.execute(query, (fromcity, fromairport, fromdate, todate, tocity, toairport))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if (data):
        return render_template('searchCustomer.html', results=data)
    else:
        error = 'No results found'
        return render_template('searchCustomer.html', error=error)

# Customer Tracks Spending BAR CHART!!!
@app.route('/homeCustomer/trackMySpending')
def trackMySpending():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT sum(price) as total \
        FROM purchases, ticket, flight \
        WHERE purchases.ticket_id = ticket.ticket_id \
        AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
        AND purchases.purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE() \
        AND purchases.customer_email = %s'
    cursor.execute(query, (username))
    total = cursor.fetchone()
    # Six month bar chart data
    currentmonth = datetime.datetime.now().month
    monthlySpending = ''


    query = 'SELECT year, month, sum(price) as monthlySpending \
            FROM (SELECT year(purchases.purchase_date) AS year, month(purchases.purchase_date) AS month, price \
                FROM purchases, ticket, flight \
                WHERE purchases.ticket_id = ticket.ticket_id \
                AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                AND (purchases.purchase_date between (CURDATE() - interval 6 month) and CURDATE())\
                AND purchases.customer_email = %s ) as a\
            GROUP BY year, month'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for i in data:
        monthlySpending += str(i[2]) + ' ' + str(i[0]) + '-' +str(i[1]) + ','
    print(monthlySpending)
    cursor.close()
    return render_template('trackSpendingCustomer.html', totalamount=total[0], results=monthlySpending)

@app.route('/homeCustomer/trackSpendingSpecific', methods=['POST'])
def trackSpendingSpecific():
    username = session['username']
    cursor = conn.cursor()
    fromdate = request.form['fromdate']
    todate = request.form['todate']
    # Get total amount of money spent in the given period
    queryGetTotal = 'SELECT sum(price) as total \
        FROM purchases, ticket, flight \
        WHERE purchases.ticket_id = ticket.ticket_id \
        AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
        AND purchases.purchase_date BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) \
        AND purchases.customer_email = %s'
    cursor.execute(queryGetTotal, (fromdate, todate, username))
    totalMoney = cursor.fetchone()
    # Six month bar chart data
    monthlySpending = ''

    query = 'SELECT year, month, sum(price) as monthlySpending \
            FROM (SELECT year(purchases.purchase_date) AS year, month(purchases.purchase_date) AS month, price \
                FROM purchases, ticket, flight \
                WHERE purchases.ticket_id = ticket.ticket_id \
                AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                AND (purchases.purchase_date between %s and %s)\
                AND purchases.customer_email = %s ) as a\
            GROUP BY year, month'
    cursor.execute(query, (fromdate, todate, username))
    data = cursor.fetchall()
    for i in data:
        monthlySpending += str(i[2]) + ' ' + str(i[0]) + '-' +str(i[1]) + ','
    cursor.close()
    return render_template('trackSpending.html', fromdate=fromdate, todate=todate, total=totalMoney[0], results=monthlySpending)

#------------------------------------------------------------------------------------------------------------
@app.route('/homeAgent')
def homeAgent():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT purchases.customer_email, purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight, booking_agent \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
                AND booking_agent.booking_agent_id = purchases.booking_agent_id \
				AND booking_agent.email = \'{}\'\
				AND departure_time > curdate() \
				ORDER BY customer_email'
    cursor.execute(query.format(username))
    data = cursor.fetchall() 
    cursor.close()
    message = request.args.get('message')
    return render_template('homeAgent.html', username=username, posts=data, message=message)

@app.route('/homeAgent/viewFlightAgent', methods=['POST'])
def viewFlightAgent():
    username = session['username']
    cursor = conn.cursor()
    fromdate = request.form['fromdate']
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    todate = request.form['todate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']

    query = 'SELECT purchases.customer_email, purchases.ticket_id, ticket.airline_name, ticket.flight_num, departure_airport, departure_time, arrival_airport, arrival_time \
				FROM purchases, ticket, flight, airport, booking_agent \
				WHERE purchases.ticket_id = ticket.ticket_id \
				AND ticket.airline_name = flight.airline_name \
				AND ticket.flight_num = flight.flight_num \
                AND flight.departure_airport = airport.airport_name \
                AND booking_agent.booking_agent_id = purchases.booking_agent_id \
				AND booking_agent.email = %s\
                AND flight.departure_time BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) \
                AND airport.airport_city = %s AND airport.airport_name = %s \
                AND (flight.airline_name, flight.flight_num) in \
                    (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                    WHERE airport.airport_name=flight.arrival_airport \
                    AND airport.airport_city = %s \
                    AND airport.airport_name = %s)'

    cursor.execute(query, (username, fromdate, todate, fromcity, fromairport, tocity, toairport))
    # Get flight information in the given period
    data = cursor.fetchall() 
    cursor.close()
    if (data):
        return render_template('viewFlightAgent.html', username=username, fromdate=fromdate, todate=todate, posts=data)
    else:
        error = 'No results found'
        return render_template('viewFlightAgent.html', username=username, fromdate=fromdate, todate=todate, error=error) 

# Agent purchases
@app.route('/homeAgent/purchasePageAgent')
def purchasePageAgent():
    return render_template('purchaseAgent.html')

@app.route('/homeAgent/searchPurchaseAgent', methods=['POST'])
def searchPurchaseAgent():
    cursor = conn.cursor()
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    fromdate = request.form['fromdate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']
    todate = request.form['todate']
    query = 'SELECT * FROM flight, airport \
            WHERE airport.airport_name = flight.departure_airport \
            AND airport.airport_city = %s \
            AND airport.airport_name = %s \
            AND flight.status = "Upcoming"\
            AND %s BETWEEN DATE_SUB(flight.departure_time, INTERVAL 2 DAY) AND DATE_ADD(flight.departure_time, INTERVAL 2 DAY) \
            AND %s BETWEEN DATE_SUB(flight.arrival_time, INTERVAL 2 DAY) AND DATE_ADD(flight.arrival_time, INTERVAL 2 DAY) \
            AND (flight.airline_name, flight.flight_num) in \
                (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                WHERE airport.airport_name=flight.arrival_airport \
                AND airport.airport_city = %s \
                AND airport.airport_name = %s)'
    cursor.execute(query, (fromcity, fromairport, fromdate, todate, tocity, toairport))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if (data):
        return render_template('purchaseAgent.html', results=data)
    else:
        error = 'No results found'
        return render_template('purchaseAgent.html', searchError=error) 

@app.route('/homeAgent/purchaseAgent', methods=['POST'])
def purchaseAgent():
    username = session['username']
    customer_email = request.form['customer_email']
    cursor = conn.cursor()
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    # Find the number of tickets to generate the next ticket_id
    queryCount = 'SELECT COUNT(*) as count FROM ticket'
    cursor.execute(queryCount)
    ticketCount = cursor.fetchone()
    ticket_id = ticketCount[0] + 1
    # Create the new ticket
    queryNewTicket = 'INSERT INTO ticket VALUES(%s, %s, %s)'
    cursor.execute(queryNewTicket, (ticket_id, airline_name, flight_num))
    # Get booking_agent_id
    queryGetID = 'SELECT booking_agent_id FROM booking_agent WHERE email=%s'
    cursor.execute(queryGetID, username)
    agentID = cursor.fetchone() # returns a dict 
    # Finalize the purchase
    queryPurchase = 'INSERT INTO purchases VALUES(%s, %s, %s, CURDATE())'
    cursor.execute(queryPurchase, (ticket_id, customer_email, agentID[0]))
    data = cursor.fetchone()
    conn.commit()
    cursor.close()
    # error = None
    return redirect(url_for('homeAgent', message = 'Successfully Purchased a Ticket!'))

# Agent searches
@app.route('/homeAgent/searchPageAgent')
def searchPageAgent():
    return render_template('searchAgent.html')

@app.route('/homeAgent/searchAgent', methods=['POST'])
def searchAgent():
    username = session['username']
    cursor = conn.cursor()
    fromcity = request.form['fromcity']
    fromairport = request.form['fromairport']
    fromdate = request.form['fromdate']
    tocity = request.form['tocity']
    toairport = request.form['toairport']
    todate = request.form['todate']
    queryGetID = 'SELECT booking_agent_id FROM booking_agent WHERE email=%s'
    cursor.execute(queryGetID, username)
    agentID = cursor.fetchone()[0]

    query = 'SELECT * FROM flight, airport \
            WHERE airport.airport_name = flight.departure_airport \
            AND airport.airport_city = %s \
            AND airport.airport_name = %s \
            AND flight.status = "Upcoming"\
            AND %s BETWEEN DATE_SUB(flight.departure_time, INTERVAL 2 DAY) AND DATE_ADD(flight.departure_time, INTERVAL 2 DAY) \
            AND %s BETWEEN DATE_SUB(flight.arrival_time, INTERVAL 2 DAY) AND DATE_ADD(flight.arrival_time, INTERVAL 2 DAY) \
            AND (flight.airline_name, flight.flight_num) in \
                (SELECT flight.airline_name, flight.flight_num FROM flight, airport \
                WHERE airport.airport_name=flight.arrival_airport \
                AND airport.airport_city = %s \
                AND airport.airport_name = %s)'
    cursor.execute(query, (fromcity, fromairport, fromdate, todate, tocity, toairport))

    data = cursor.fetchall()
    cursor.close()
    error = None
    if (data):
        return render_template('searchAgent.html', results=data)
    else:
        #returns an error message to the html page
        error = 'No results found'
        return render_template('searchAgent.html', error=error)   

# Agent view commission
@app.route('/homeAgent/viewMyCommission')
def viewMyCommission():
    username = session['username']
    cursor = conn.cursor()
    # Get booking_agent_id
    queryGetID = 'SELECT booking_agent_id FROM booking_agent WHERE email=%s'
    cursor.execute(queryGetID, username)
    agentID = cursor.fetchone()
    # Get total commsion in the past 30 days
    queryGetCommission = 'SELECT sum(price)*.10 as totalComm FROM purchases, ticket, flight \
                            WHERE purchases.ticket_id = ticket.ticket_id \
                            AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                            AND purchases.purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE() \
                            AND purchases.booking_agent_id = %s'
    cursor.execute(queryGetCommission, agentID[0])
    totalComm = cursor.fetchone()
    totalCommVal = 0
    if totalComm[0] != None:
        totalCommVal = totalComm[0]
    # Get total tickets in the past 30 days 
    queryGetTicketCount = 'SELECT count(*) as ticketCount FROM purchases, ticket, flight \
                            WHERE purchases.ticket_id = ticket.ticket_id \
                            AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                            AND purchases.purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE() \
                            AND purchases.booking_agent_id = %s'
    cursor.execute(queryGetTicketCount, agentID[0])
    ticketCount = cursor.fetchone()
    ticketCountVal = ticketCount[0]
    avgComm = 0
    # print ticketCount, totalCommVal
    if ticketCountVal != 0:
        avgComm = totalCommVal/ticketCountVal
    cursor.close()  
    return render_template('viewCommissionAgent.html', username=username, totalComm=totalCommVal, avgComm=avgComm, ticketCount=ticketCountVal)      

@app.route('/homeAgent/commission', methods=['POST'])
def commission():
    username = session['username']
    cursor = conn.cursor()
    fromdate = request.form['fromdate']
    todate = request.form['todate']

    queryGetID = 'SELECT booking_agent_id FROM booking_agent WHERE email=%s'
    cursor.execute(queryGetID, username)
    agentID = cursor.fetchone()
    # Get total commsion in the given period
    queryGetCommission = 'SELECT sum(price)*.10 as totalComm FROM purchases, ticket, flight \
                            WHERE purchases.ticket_id = ticket.ticket_id \
                            AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                            AND purchases.purchase_date BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) \
                            AND purchases.booking_agent_id = %s'
    cursor.execute(queryGetCommission, (fromdate, todate, agentID[0]))
    totalComm = cursor.fetchone()
    totalCommVal = 0
    if totalComm[0] != None:
        totalCommVal = totalComm[0]
    # Get total tickets in the given period
    queryGetTicketCount = 'SELECT count(*) as ticketCount FROM purchases, ticket, flight \
                            WHERE purchases.ticket_id = ticket.ticket_id \
                            AND ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num \
                            AND purchases.purchase_date BETWEEN CAST(%s AS DATE) AND CAST(%s AS DATE) \
                            AND purchases.booking_agent_id = %s'
    cursor.execute(queryGetTicketCount, (fromdate, todate, agentID[0]))
    ticketCount = cursor.fetchone()
    ticketCountVal = ticketCount[0]
    cursor.close()
    return render_template('commission.html', fromdate=fromdate, todate=todate, totalComm=totalCommVal, ticketCount=ticketCountVal)

# Agent view Top 5 Customers
@app.route('/homeAgent/viewTop5Customers')
def viewTop5Customers():
    username = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT customer_email, count(ticket_id) as ticket_sales\
                FROM booking_agent NATURAL JOIN purchases\
                WHERE (purchase_date between date_sub(curdate(), interval 6 month) and curdate())\
                    and email = %s\
                group by customer_email\
                order by ticket_sales DESC\
                limit 5'
    cursor.execute(query1, (username))
    data1 = cursor.fetchall()
    ticketTop5 = ''
    for i in data1:
        ticketTop5 += str(i[1]) + " " + str(i[0]) + ","
    query2 = 'SELECT customer_email, sum(flight.price) as commission\
                FROM booking_agent, purchases, ticket, flight\
                WHERE (purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
                    AND booking_agent.booking_agent_id = purchases.booking_agent_id \
                    AND purchases.ticket_id = ticket.ticket_id \
                    AND ticket.airline_name = flight.airline_name \
                    AND ticket.flight_num = flight.flight_num \
                    AND booking_agent.email = %s\
                group by purchases.customer_email\
                order by commission DESC\
                limit 5'
    cursor.execute(query2, (username))
    data2 = cursor.fetchall()
    commissionTop5 = ''
    for i in data2:
        commissionTop5 += str(i[1]) + " " + str(i[0]) + ","
    print(commissionTop5)
    return render_template('viewTop5Customers.html', results1=ticketTop5, results2=commissionTop5)

#Coco's
def validateDates(begindate, enddate):
    begin = datetime.datetime.strptime(begindate, '%Y-%m-%d')
    end = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    return begin <= end

def validateTime(begintime, endtime):
    #print(begintime, endtime)
    begindate = datetime.datetime.strptime(begintime, '%Y-%m-%dT%H:%M')
    enddate = datetime.datetime.strptime(endtime, '%Y-%m-%dT%H:%M')
    return begindate <= enddate

@app.route('/publicsearch')
def searchpage():
    error = request.args.get('error')
    return render_template('publicsearch.html', error=error)

@app.route('/searchresult/flight', methods=['POST'])
def searchUpcomingFlights():
    cursor = conn.cursor()
    searchtext1 = request.form['departurecity']
    searchtext2 = request.form['arrivalcity']
    searchtext3 = request.form['departuredate']
    query = 'select * from flight\
             where (departure_airport = %s \
                    or departure_airport in (select airport_name from airport where airport_city = %s))\
                    and (arrival_airport = %s \
                    or arrival_airport in (select airport_name from airport where airport_city = %s))\
                    and convert(departure_time,date) = %s\
                    and status = "upcoming"\
                    and (departure_time >= curtime() or arrival_time >= curtime())'
    cursor.execute(query, (searchtext1,searchtext1,searchtext2,searchtext2,searchtext3))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if data:
        return render_template('searchresult.html', results=data)
    else:
        error = 'No results found'
        return redirect(url_for('hello', error=error))

@app.route('/searchresult/status', methods=['POST'])
def searchForStatus():
    flightnumber = request.form['flightnumberbox']
    doradate = request.form['doradate']
    
    cursor = conn.cursor()
    query = 'select airline_name,flight_num, status, departure_time, arrival_time from flight\
             where flight_num=%s\
             and (convert(departure_time,date)=%s or convert(arrival_time,date)=%s)\
             and (departure_time >= curtime() or arrival_time >= curtime())'
    cursor.execute(query, (flightnumber,doradate,doradate))
    data = cursor.fetchall()
    print(data)
    cursor.close()
    error = None
    if data:
        return render_template('statusresult.html', results=data)
    else:
        error = 'No results found'
        return redirect(url_for('hello', error=error))

def staffvalidation():
    try:
        #could be that there is no user, make sure
        username = session['username']
    except:
        return False
    
    cursor = conn.cursor()
    query = 'select * from airline_staff where username=%s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    if data:
        return True
    else:
        #Logout before returning error message
        session.pop('username')
        return False

def staffairline():
    username = session['username']
    cursor = conn.cursor()
    query = 'select airline_name from airline_staff where username = %s'
    cursor.execute(query, (username))
    #fetchall returns an array, each element is a dictionary
    airline = cursor.fetchone()
    cursor.close()
    
    return airline

# @app.route('/staffHome')
# def staffHome():
#     if staffvalidation():
#         username = session['username']
#         message = request.args.get('message')
#         #username = "coco"
#         return render_template('staffhome.html', username=username, message=message)
#     else:
#         error = 'Invalid credentials, please login again!!'
#         return redirect(url_for('hello', error=error))

# @app.route('/staffHome/searchFlights')
@app.route('/staffHome')
def staffHome():
    if staffvalidation():
        username = session['username']
        cursor = conn.cursor()
        airline = staffairline()
        query = 'select * from flight where airline_name = %s\
                 and status = "upcoming"\
                 and ((departure_time between curdate() and date_add(curdate(), interval 30 day)) or (arrival_time between curdate() and date_add(curdate(), interval 30 day)))'
                 #and departure_time between "2020-12-12" and "2021-01-12"'
        cursor.execute(query, (airline))
        data = cursor.fetchall()
        cursor.close()

        error = request.args.get('error')
        message2= request.args.get('message2')
        return render_template('staffsearchflight.html',username=username,error=error,results=data,message2=message2,message='Upcoming flights for the next 30 days:')
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/searchFlights/filter', methods=['POST'])
def staffsearchresult_filter():
    if staffvalidation():
        username = session['username']
        cursor = conn.cursor()
        airline = staffairline()
        dcity = request.form['departurecitybox']
        acity = request.form['arrivalcitybox']
        fromdate = request.form['begin']
        todate = request.form['end']

        if not validateDates(fromdate, todate):
            error = 'Invalid date range'
            return redirect(url_for('staffHome', error=error))

        if dcity == 'None' and acity == 'None':
            query = 'select * from flight where airline_name = %s\
                    and ((convert(departure_time,date) between %s and %s)\
                        or (convert(arrival_time,date) between %s and %s))'
            cursor.execute(query, (airline,fromdate,todate,fromdate,todate))
            data = cursor.fetchall()
            cursor.close()
        elif dcity == 'None':
            query = 'select * from flight where airline_name = %s\
                    and (arrival_airport = %s \
                        or arrival_airport in (select airport_name from airport where airport_city = %s))\
                    and ((convert(departure_time,date) between %s and %s)\
                        or (convert(arrival_time,date) between %s and %s))'
            cursor.execute(query, (airline,acity,acity,fromdate,todate,fromdate,todate))
            data = cursor.fetchall()
            cursor.close()
        elif acity == 'None':
            query = 'select * from flight where airline_name = %s\
                    and (departure_airport = %s \
                        or departure_airport in (select airport_name from airport where airport_city = %s))\
                    and ((convert(departure_time,date) between %s and %s)\
                        or (convert(arrival_time,date) between %s and %s))'
            cursor.execute(query, (airline,dcity,dcity,fromdate,todate,fromdate,todate))
            data = cursor.fetchall()
            cursor.close()
        else:
            query = 'select * from flight where airline_name = %s\
                    and (departure_airport = %s \
                        or departure_airport in (select airport_name from airport where airport_city = %s))\
                    and (arrival_airport = %s \
                        or arrival_airport in (select airport_name from airport where airport_city = %s))\
                    and ((convert(departure_time,date) between %s and %s)\
                        or (convert(arrival_time,date) between %s and %s))'
            cursor.execute(query, (airline,dcity,dcity,acity,acity,fromdate,todate,fromdate,todate))
            data = cursor.fetchall()
            cursor.close()
        error = None
        if data:
            return render_template('staffsearchflight.html', username=username,results=data,message='Here is the filter result:')
        else:
            #returns an error message to the html page
            error = 'No results found'
            return redirect(url_for('staffHome', error=error))
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/searchFlights/customers', methods=['POST'])
def staffsearchresult_customers():
    if staffvalidation():
        username = session['username']
        cursor = conn.cursor()
        airline = staffairline()
        flightnum = request.form['flightnumberbox']
        cursor = conn.cursor()
        query = 'select customer_email from purchases natural join ticket where flight_num = %s and airline_name=%s'
        cursor.execute(query, (flightnum, airline))
        data = cursor.fetchall()
        cursor.close()
        if data:
            return render_template('staffsearchflight.html', username=username,customerresults=data,message='Customers on Flight '+flightnum)
        else:
            #returns an error message to the html page
            error = 'No results found'
            return redirect(url_for('staffHome', error=error))
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/searchFlights/updateFlight')
def createflightbegin():
    if staffvalidation():     
        error = request.args.get('error')
        return render_template('createflight.html', error=error)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/searchFlights/updatedlist', methods=['POST'])
def createflight():
    if staffvalidation():     
        flightnum = request.form['flightnum']
        departport = request.form['departport']
        departtime = request.form['departtime']
        arriveport = request.form['arriveport']
        arrivetime = request.form['arrivetime']
        price = request.form['price']
        status = "Upcoming"
        airplaneid = request.form['airplanenum']

        if not validateTime(departtime, arrivetime):
            error = 'Invalid date range'
            return redirect(url_for('createflightbegin', error=error))

        airline = staffairline()
        cursor = conn.cursor()
        query = 'select * from airplane where airplane_id = %s and airline_name = %s'
        cursor.execute(query, (airplaneid, airline))
        data = cursor.fetchall()
        if not data:
            error = 'Invalid Airplane ID'
            return redirect(url_for('createflightbegin', error=error))
        
        query2 = 'select * from airport where airport_name=%s'
        cursor.execute(query2, (departport))
        data2 = cursor.fetchall()
        if not data2:
            error = 'Invalid Departport'
            return redirect(url_for('createflightbegin', error=error))
        
        query3 = 'select * from airport where airport_name=%s'
        cursor.execute(query3, (arriveport))
        data3 = cursor.fetchall()
        if not data3:
            error = 'Invalid Arrivalport'
            return redirect(url_for('createflightbegin', error=error))
        

        query = 'insert into flight values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (airline, flightnum, departport, departtime, arriveport, arrivetime, price, status, airplaneid))
        conn.commit()
        cursor.close()

        # cursor1 = conn.cursor()
        # query1 = 'select * from flight where airline_name = %s\
        #          and status = "upcoming"\
        #          and departure_time between "2020-12-12" and "2021-01-12"'
        #          #and ((departure_time between curdate() and date_add(curdate(), interval 30 day)) or (arrival_time between curdate() and date_add(curdate(), interval 30 day)))'

        # cursor1.execute(query1, (airline))
        # data1 = cursor1.fetchall()
        # cursor1.close()

        error = request.args.get('error')
        flash('Updated Successfully!')
        return redirect(url_for('staffHome',error=error))

    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/searchFlights/updatedstatus', methods=['POST'])
def changeflightstatus():
    if staffvalidation(): 
        cursor = conn.cursor()
        flightnum = request.form['flightnum']
        status = request.form['status']

        airline = staffairline()
    
        query = 'select * from flight where flight_num = %s and airline_name = %s'
        cursor.execute(query, (flightnum, airline))
        data = cursor.fetchall()
        if not data:
            error = 'Incorrect permission - can only change flights from your airline'
            return redirect(url_for('createflightbegin', error=error))
        
        query1 = 'update flight set status=%s where flight_num=%s and airline_name = %s'
        cursor.execute(query1, (status, flightnum, airline))
        conn.commit()
        cursor.close()

        error = request.args.get('error')
        flash('Successfully Updated!')
        return redirect(url_for('staffHome',error=error))

    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/addAirplane')
def addairplane():
    if staffvalidation():
        error = request.args.get('error')
        return render_template('addairplane.html', error=error)   
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/addAirplane/confirmation', methods=['POST'])
def addairplaneconfirm():
    if staffvalidation(): 
        cursor = conn.cursor()
        airplaneid = request.form['id']
        seats = request.form['seats']
        airline = staffairline()

        query = 'select * from airplane where airplane_id = %s'
        cursor.execute(query, (airplaneid))
        data = cursor.fetchall()

        if data:
            return redirect(url_for('addairplane', error = 'This airplane already existed'))
        
        query1 = 'insert into airplane values (%s, %s, %s)'
        cursor.execute(query1, (airline, airplaneid, seats))
        conn.commit()

        query2 = 'select * from airplane where airline_name = %s'
        cursor.execute(query2, (airline))
        data = cursor.fetchall()
        cursor.close()
        flash('Successfully add!')
        return render_template('addairplaneresult.html',results=data)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/addAirport')
def addairport():
    if staffvalidation():
        error = request.args.get('error')
        return render_template('addairport.html', error=error)     
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))
    
@app.route('/staffHome/addAirport/confirmation', methods=['POST'])
def addairportconfirm():
    if staffvalidation(): 
        cursor = conn.cursor()
        airport = request.form['airport']
        city = request.form['city']

        query = 'select * from airport where airport_name = %s'
        cursor.execute(query, (airport))
        data = cursor.fetchall()

        if data:
            return redirect(url_for('addairport', error = 'This airport already existed'))
        
        query1 = 'insert into airport values (%s, %s)'
        cursor.execute(query1, (airport, city))
        conn.commit()
        cursor.close()

        flash('Successfully add!')
        return redirect(url_for('staffHome', message2='Successfully add an airport!'))
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewBookingagents')
def viewbookingagents():
    if staffvalidation():
        airline = staffairline()

        cursor = conn.cursor()
        query1 = 'select email, count(ticket_id) as ticket_sales\
                  from booking_agent natural join purchases natural join ticket\
                  where (purchase_date between date_sub(curdate(), interval 1 month) and curdate())\
                        and airline_name = %s\
                  group by email\
                  order by ticket_sales DESC\
                  limit 5'
        cursor.execute(query1, (airline))
        data1 = cursor.fetchall()

        query2 = 'select email, count(ticket_id) as ticket_sales\
                  from booking_agent natural join purchases natural join ticket\
                  where (purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
                        and airline_name = %s\
                  group by email\
                  order by ticket_sales DESC\
                  limit 5'
        cursor.execute(query2, (airline))
        data2 = cursor.fetchall()

        query3 = 'select email, sum(price)*0.1 as totalcommission\
                  from booking_agent natural join purchases natural join ticket natural join flight\
                  where (purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
                        and airline_name = %s\
                  group by email\
                  order by totalcommission DESC\
                  limit 5'
        cursor.execute(query3, (airline))
        data3 = cursor.fetchall()
        cursor.close()
        #print(data1, data2,data3)
        
        error = request.args.get('error')
        return render_template('viewbookingagents.html', error=error, results1=data1, results2=data2, results3=data3)     
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewCustomers')
def viewcustomers():
    if staffvalidation():
        airline = staffairline()

        cursor = conn.cursor()
        query = 'select customer.name, purchases.customer_email, count(ticket.ticket_id) as ticket_purchased\
                 from (purchases natural join ticket), customer\
                 where customer.email = purchases.customer_email\
                       and ticket.airline_name = %s\
                       and (purchases.purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
                 group by purchases.customer_email\
                 order by ticket_purchased DESC\
                 limit 1'

        cursor.execute(query, (airline))
        data = cursor.fetchall()
        cursor.close()
        #print(data)
        error = request.args.get('error')
        return render_template('viewcustomers.html', error=error, results=data)     
        
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewCustomers/particular', methods=['POST'])
def viewcustomers_filter():
    if staffvalidation():
        airline = staffairline()
        customer = request.form['email']

        cursor = conn.cursor()
        query = 'select distinct flight_num from purchases natural join ticket where airline_name = %s and customer_email=%s'
        cursor.execute(query, (airline, customer))
        data = cursor.fetchall()
        cursor.close()
        error = request.args.get('error')
        return render_template('viewcustomerfilter.html', error=error, results=data, customer=customer)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewReports')
def viewreports():
    if staffvalidation():
        airline = staffairline()
        yearlyticketsales = ''
        cursor = conn.cursor()
        query = 'select year,month,count(ticket_id)\
                from (select year(purchase_date) as year, month(purchase_date) as month, ticket_id\
                from purchases natural join ticket\
                where (purchase_date between date_sub(curdate(), interval 1 year) and curdate()) and airline_name = %s) as a\
                group by year, month'
        cursor.execute(query, (airline))
        data = cursor.fetchall()
        for i in data:
            yearlyticketsales += str(i[0]) + '-' +str(i[1])+' '+ str(i[2]) + ','

        print(yearlyticketsales)
        cursor.close()
        error = request.args.get('error')
        return render_template('viewreport.html', error=error) #results=yearlyticketsales
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewReports/range', methods=['POST'])
def viewreportresult1():
    if staffvalidation():
        airline = staffairline()
        begindate = request.form['begindate']
        enddate = request.form['enddate']

        if not validateDates(begindate, enddate):
            error = 'Invalid date range'
            return redirect(url_for('viewreports', error=error))

        cursor = conn.cursor()
        query = 'select count(ticket_id) as sales from purchases natural join ticket where airline_name=%s and purchase_date between %s and %s'
        cursor.execute(query, (airline, begindate, enddate))
        data1 = cursor.fetchall()
        cursor.close()

        yearlyticketsales = ''
        cursor = conn.cursor()
        query = 'select year,month,count(ticket_id)\
                from (select year(purchase_date) as year, month(purchase_date) as month, ticket_id\
                from purchases natural join ticket\
                where (purchase_date between %s and %s) and airline_name = %s) as a\
                group by year, month'
        cursor.execute(query, (begindate, enddate,airline))
        data = cursor.fetchall() 
        for i in data:
            yearlyticketsales += str(i[0]) + '-' +str(i[1])+' '+ str(i[2]) + ','

        print(yearlyticketsales)
        cursor.close()
        
        return render_template('viewreport.html', message='Tickets sold between ' +begindate+' and '+enddate+ ' is '+str(data1[0][0])+'.',results=yearlyticketsales)
    
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewReports/time', methods=['POST'])
def viewreportresult2():
    if staffvalidation():
        airline = staffairline()
        period = request.form['period']

        cursor = conn.cursor()
        query = 'select count(ticket_id) as sales from purchases natural join ticket where airline_name=%s and (purchase_date between date_sub(curdate(), interval 1 ' + period + ') and curdate())'
        cursor.execute(query, (airline))
        data1 = cursor.fetchall()
        cursor.close()

        yearlyticketsales = ''
        cursor = conn.cursor()
        query = 'select year,month,count(ticket_id)\
                from (select year(purchase_date) as year, month(purchase_date) as month, ticket_id\
                from purchases natural join ticket\
                where (purchase_date between date_sub(curdate(), interval 1 ' + period + ') and curdate()) and airline_name = %s) as a\
                group by year, month'
        cursor.execute(query, (airline))
        data = cursor.fetchall() 
        for i in data:
            yearlyticketsales += str(i[0]) + '-' +str(i[1])+' '+ str(i[2]) + ','

        print(yearlyticketsales)
        cursor.close()

        
        return render_template('viewreport.html', message='Tickets sold last '+ period+' is '+str(data1[0][0])+'.',results=yearlyticketsales)
    
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewDestinations')
def viewdestinations():
    if staffvalidation():
        airline = staffairline()
        cursor = conn.cursor()
        query1 = 'select flight.arrival_airport, airport.airport_city, count(*) as total_purchase\
                 from (flight natural join purchases natural join ticket),airport \
                 where flight.arrival_airport = airport.airport_name and ticket.airline_name = %s and purchases.purchase_date between date_sub(curdate(), interval 3 month) and curdate()\
                 group by flight.arrival_airport, airport.airport_city\
                 order by count(*) DESC\
                 limit 3'
        cursor.execute(query1, (airline))
        data1 = cursor.fetchall()
        query2 = 'select flight.arrival_airport, airport.airport_city, count(*) as total_purchase\
                 from (flight natural join purchases natural join ticket),airport \
                 where flight.arrival_airport = airport.airport_name and ticket.airline_name = %s and purchases.purchase_date between date_sub(curdate(), interval 1 year) and curdate()\
                 group by flight.arrival_airport, airport.airport_city\
                 order by count(*) DESC\
                 limit 3'
        cursor.execute(query2, (airline))
        data2 = cursor.fetchall()
        cursor.close()
        return render_template('viewdestination.html', results1=data1, results2=data2)
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/staffHome/viewRevenues')
def viewrevenues():
    if staffvalidation():
        airline = staffairline()
        cursor = conn.cursor()
        query1 = 'select sum(price)\
                  from flight natural join purchases natural join ticket\
                  where airline_name = %s and (purchase_date between date_sub(curdate(), interval 1 month) and curdate())\
	              and booking_agent_id is null'
        cursor.execute(query1, (airline))
        data1 = cursor.fetchall()
        query2 = 'select sum(price)\
                  from flight natural join purchases natural join ticket\
                  where airline_name = %s and (purchase_date between date_sub(curdate(), interval 1 month) and curdate())\
	              and booking_agent_id is not null'
        cursor.execute(query2, (airline))
        data2 = cursor.fetchall()
        query3 = 'select sum(price)\
                  from flight natural join purchases natural join ticket\
                  where airline_name = %s and (purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
	              and booking_agent_id is null'
        cursor.execute(query3, (airline))
        data3 = cursor.fetchall()
        query4 = 'select sum(price)\
                  from flight natural join purchases natural join ticket\
                  where airline_name = %s and (purchase_date between date_sub(curdate(), interval 1 year) and curdate())\
	              and booking_agent_id is not null'
        cursor.execute(query4, (airline))
        data4 = cursor.fetchall()
        cursor.close()

        return render_template('viewrevenue.html', mdirect=data1[0][0], mindirect=data2[0][0],ydirect=data3[0][0],yindirect=data4[0][0])
    else:
        error = 'Invalid credentials, please login again!!'
        return redirect(url_for('hello', error=error))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')

app.secret_key = 'cocoandkrystalsdbproject'

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
