from project.app import db

class Event(db.Model):
    Event_ID = db.Column(db.Integer, primary_key=True)
    Event_Name = db.Column(db.String(255), nullable=False)
    #name = db.Column(db.String(255), nullable=False)
    #email = db.Column(db.String(255), nullable=False)
    #username = db.Column(db.String(255), nullable=False)
    Coordinator_Name = db.Column(db.String(255), nullable=False)
    Coordinator_Email = db.Column(db.String(255), nullable=False)
    Coordinator_UtorID = db.Column(db.String(255), nullable=False)
    Organization_Name = db.Column(db.Text, nullable=False)
    Target_Campus = db.Column(db.String(255), nullable=False)
    Event_Description = db.Column(db.String(255), nullable=False)
    Event_Month = db.Column(db.String(20), nullable=False)
    Event_Date = db.Column(db.Integer, nullable=False)
    Event_Year = db.Column(db.Integer, nullable=False)
    Event_Start_Time = db.Column(db.Time, nullable=False)
    Event_End_Time = db.Column(db.Time, nullable=False)
    
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, Event_ID, Event_Name, Coordinator_Name, Coordinator_Email, 
                 Coordinator_UtorID, Organization_Name, Target_Campus, Event_Description, 
                 Event_Month, Event_Date, Event_Year, Event_Start_Time, Event_End_Date):
        self.Event_ID = Event_ID
        self.Event_Name = Event_Name
        self.Coordinator_Name = Coordinator_Name
        self.Coordinator_Email = Coordinator_Email
        self.Coordinator_UtorID = Coordinator_UtorID
        self.Organization_Name = Organization_Name
        self.Target_Campus = Target_Campus
        self.Event_Description = Event_Description
        self.Event_Month = Event_Month
        self.Event_Date = Event_Date
        self.Event_Year = Event_Year
        self.Event_Start_Time = Event_Start_Time
        self.Event_End_Date = Event_End_Date

    def __repr__(self):
        return f"<title {self.title}>"
