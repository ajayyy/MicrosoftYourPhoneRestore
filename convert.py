import sqlite3, re, base64
from xml.etree.ElementTree import Element, SubElement, tostring

phoneNumberFile = open('phoneNumber.properties')
phoneNumber = phoneNumberFile.read()
phoneNumberFile.close()

def init(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    db = conn.cursor()

    # Get sms message info from the db
    db.execute("SELECT * FROM message")
    messageRows = db.fetchall()

    # Create top element
    topElement = Element('smses', {'count': str(len(messageRows))}) 

    for messageRow in messageRows:
        convertSMS(messageRow, db, topElement)
    
    # Get mms message info from the db
    db.execute("SELECT * FROM mms")
    mmsRows = db.fetchall()

    for mmsRow in mmsRows:
        convertMMS(mmsRow, db, topElement)

    result = tostring(topElement)

    # Save the result file
    file = open('./output/sms.xml', 'w+')
    file.write(str(result))
    file.close()
    

def convertSMS(messageRow, db, topElement):
    protocol = "0"

    address = messageRow[3]
    # This will happen when there is a sent message
    if address == "":
        # Get the address from the conversation table
        db.execute("SELECT recipient_list FROM conversation WHERE thread_id = ?", (messageRow[1],))
        address = db.fetchone()[0]
        # This number may contain +1 in it
        if len(address) > 10:
            address = address[(len(address) - 11):]

    # The date is stored more precisely by Microsoft
    date = str(int(messageRow[7] / 10000) - 11644473600000)

    #just called type in xml
    messageType = str(messageRow[4])

    subject = "null"
    body = messageRow[6]
    toa = "null"
    sc_toa = "null"
    service_center = "null"
    read = "1"
    status = "-1"
    locked = "0"

    # Now save this data into the XML
    messageXML = SubElement(topElement, 'sms', {'protocol': protocol, 'address': address, 'date': date, 'type': messageType, 
        'subject': subject, 'body': body, 'toa': toa, 'sc_toa': sc_toa, 'service_center': service_center, 'read': read, 
        'status': status, 'locked': locked})

def convertParts(messageRow, db, topElement):
    # Get a list of the parts from this conversation
    db.execute("SELECT * FROM mms_part WHERE message_id = ?", (messageRow[0],))
    parts = db.fetchall()
    
    for part in parts:
        seq = str(part[2])
        ct = str(part[4])
        cid = str(part[3])
        name = str(part[6])
        chset = str(part[7])
        text = str(part[5])

        # Use the name as that should be close enough
        cl = name

        # Convert from base 64
        data = str(base64.b64encode(part[8]))

        SubElement(topElement, 'part', {'seq': seq, 'ct': ct, 'cid': cid, 'name': name, 
                'chset': chset, 'text': text, 'cl': cl, 'data': data})
        
def convertAddresses(messageRow, db, topElement):
    # Get a list of the addresses from this conversation
    db.execute("SELECT recipient_list FROM conversation WHERE thread_id = ?", (messageRow[1],))
    addresses = db.fetchone()[0].split(",")

    for address in addresses:
        address = address[0]
        messageType = "151"
        charset = "106"
        SubElement(topElement, 'addr', {'address': address, 'type': messageType, 'charset': charset})

    # Add the from address
    address = phoneNumber
    messageType = "151"
    charset = "106"
    SubElement(topElement, 'addr', {'address': address, 'type': messageType, 'charset': charset})

def convertMMS(messageRow, db, topElement):
    # The date is stored more precisely by Microsoft
    date = str(int(messageRow[7] / 100000))

    ct_t = "application/vnd.wap.multipart.related"
    msg_box = str(messageRow[3])
    rr = "null"
    sub = "null"
    read_status = "null"
    address = str(messageRow[9])
    # This number may contain +1 in it
    if len(address) > 10:
        address = address[(len(address) - 11):]
    if re.search('[a-zA-Z]', address) != None:
        # This is not a valid number since it has letters
        return

    m_id = "null"
    read = "1"
    m_size = "null"
    
    # The type is 128 if it is sent and 132 if recieved
    m_type = "132"
    if messageRow[3] == 2:
        m_type = "128"
    
    mmsElement = SubElement(topElement, 'mms', {'date': date, 'address': address, 'ct_t': ct_t, 
        'msg_box': msg_box, 'rr': rr, 'sub': sub, 'sub': sub, 'm_id': m_id, 'read': read, 
        'm_size': m_size, 'm_type': m_type})

    # Find and load the parts
    db.execute("SELECT * FROM mms_part WHERE message_id = ?", (messageRow[1],))
    parts = db.fetchall()

    # Load all of the parts
    convertParts(messageRow, db, SubElement(mmsElement, 'parts'))

    # Load all of the addresses
    convertAddresses(messageRow, db, SubElement(mmsElement, 'addrs'))

init('phone.db')