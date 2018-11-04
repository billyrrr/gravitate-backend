from google.cloud import firestore

def addToEventSchedule(db: firestore.Client, uid, scheduleOfOneEvent): 
    userRef: firestore.DocumentReference = db.collection(u'users').document(uid)
    eventSchedulesRef: firestore.CollectionReference = userRef.collection(u'eventSchedules')
    eventSchedulesRef.add(scheduleOfOneEvent)
