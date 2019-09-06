import sqlite3

def init(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    db = conn.cursor()

    # Get message info from the db
    db.execute("SELECT * FROM message")
    messageRows = db.fetchAll()

    for messageRow in messageRows:
        convertSMS(messageRow)
    

def convertSMS(messageRow):
    protocol = 0

    address = messageRow.from_address
    # This will happen when there is a sent message
    if address == "":
        # Get the address from the conversation table
        db.execute("SELECT recipient_list FROM conversation WHERE thread_id = ?", messageRow.thread_id)
        address = db.fetchone().recipient_list
        # This number may contain +1 in it
        if len(address) > 10:
            address = address[(len(address) - 11):]

    # The date is stored more precisely by Microsoft
    date = messageRow.timestamp / 100000

    type = messageRow.type
    subject = "null"
    body = messageRow.body
    toa = "null"
    sc_toa = "null"
    service_center = "null"
    read = 1
    status = -1
    locked = 0

    # Now save this data into the XML