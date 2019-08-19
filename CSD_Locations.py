from pyscopus import Scopus #using this module to retrieve the paper info.
import sqlite3 #storing the data in an SQLite file.

#Locations database (attached).
db = 'Locations.db'
connection = sqlite3.connect(db)
cursor = connection.cursor()

#we have a table of dois and dates for all refcodes (pulled straight from Conquest).
cursor.execute(
    "SELECT t1.refcode, t1.field2,t1.field3, t1.field4 FROM DOI_List t1 LEFT JOIN Locations t2 ON t2.refcode = t1.refcode WHERE t2.refcode IS NULL ")
refcodes = cursor.fetchall()
connection.close()
print len(refcodes)

#You need a SCOPUS API key to access the data.
key = ""
scopus = Scopus(key)

#for each entry...
for refcode in refcodes:
    print refcode[0]
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    row_exsists = len((cursor.execute(
        "SELECT 1 FROM Fails WHERE refcode = '%s'" % (
            refcode[0]))).fetchall()) > 0 # some errors occur, to avoid repeating them I've created a fail table to just get rid of them.
    if not row_exsists and refcode[0] != "AFUYIL":
        try:

            ref = refcode[0]
            doi = refcode[1]
            print doi
            entry_info = scopus.search(doi)
            address = ((entry_info.values)[0])[0] #here we state that we want the first author address info with [0] but you could re-write this to get all authors.
            print address
            city = (address[0])['city']
            inst = (address[0])['name']
            country = (address[0])['country']
            location_string = inst + ", " + city + ", " + country
            print ref, location_string
            cursor.execute("INSERT INTO Locations VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (ref, inst, city, country, refcode[2], refcode[3], location_string))
        except KeyError: #if the api key doesn't work. also encounters this when it can't get the paper reference.
            print "keyerror"
        except ValueError: #if no address.
            print ValueError
            cursor.execute("INSERT INTO Fails VALUES ('%s')" % ref)
        except IndexError: #no author info
            print IndexError
            cursor.execute("INSERT INTO Fails VALUES ('%s')" % ref)
        except TypeError: #
            print TypeError
            cursor.execute("INSERT INTO Fails VALUES ('%s')" % ref)
        except SyntaxError:
            print SyntaxError
            cursor.execute("INSERT INTO Fails VALUES ('%s')" % ref)
        except sqlite3.OperationalError:
            print sqlite3.OperationalError
            cursor.execute("INSERT INTO Fails VALUES ('%s')" % ref)
    connection.commit()
    connection.close()

