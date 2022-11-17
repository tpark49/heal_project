import json
import pandas as pd
from datetime import date, datetime, timedelta


class scheduler: 
    def __init__(self, start_shift_time='08:00', end_shift_time='17:00', time_zone="EST"):
        self.start_shift_time = datetime.strptime(start_shift_time, '%H:%M')
        self.end_shift_time = datetime.strptime(end_shift_time, '%H:%M') 
        self.appt_timelimit = 1
        self.time_zone = time_zone 
        self.data = None

    def load_data(self): 
        jsonFile = open("data.json", "r") 
        self.data = json.load(jsonFile) 
        jsonFile.close() 
        
        
    def update_json(self):
        jsonFile = open("data.json", "w+")
        jsonFile.write(json.dumps(self.data))
        jsonFile.close()

        
    def query_data(self,date):
        #load data
        if self.data is None: 
            self.load_data()
        #query for the corresponding date
        if not self.data.get(date):
            self.data[date] = []
        return self.data[date]
    
        
    def remove_appt(self, start, end, date): 
        if self.data is None: 
            self.load_data() 
        
        appt_data = self.query_data(date)
        
        for i in range(len(appt_data)): 
            if appt_data[i]["start"] == start and appt_data[i]["end"] == end: 
                appt_data.pop(i)
                if len(appt_data)==0: 
                    del self.data[date]
                self.update_json()
                return True 
        return False

    def update_appt(self, start, end, date, new_start, new_end, new_date):
        self.remove_appt(start, end, date)

        if self.schedule_appt(new_start, new_end, new_date) == True: 
            return True 

        else:
            self.schedule_appt(start, end, date) 
            return False


    
    def schedule_appt(self, start, end, date):
        
        #retrieve data; appt_data will be list of dictionaries 
        appt_data = self.query_data(date)

        #if there is a record of given date
        if appt_data != []: 
        
            #check if there is availability for the given appt 
            if not self.appt_possible(start, end, appt_data): 
                return False 
            
        appt_data.append({
            "start":start,
            "end": end
        })
        
        self.update_json()

        return True 
           
    
    def appt_possible(self, start, end, schedule):
        
        start = datetime.strptime(start, '%H:%M')
        end = datetime.strptime(end, '%H:%M')
        delta = end - start
        
        #if longer then limit, return false 
        if delta.seconds//3600 > self.appt_timelimit: 
            return False 
        
        #if outside of shift schedule, return false 
        if start<self.start_shift_time or end>self.end_shift_time: 
            return False
        
        #if no appt, return True 
        if len(schedule)==0: 
            return True 
        
        #sort the appt 
        appts = sorted(schedule, key=lambda x: x["start"])
        
        #iterate through appt and check for overlap  
        for appt in appts: 
            appt_start = datetime.strptime(appt["start"], '%H:%M')
            appt_end = datetime.strptime(appt["end"], '%H:%M')
            
            
            if appt_start<end<appt_end  or \
            appt_start<start<appt_end  or \
            start<appt_start<end or \
            start<appt_end <end:
                return False
            
            #since list is sorted, the remainder of the iteration is irrelevant 
            if end<=appt_start:
                return True 
            
        return True 
       
    def show_calendar(self, date, delta=[0,0]):
        if self.data is None: 
            self.load_data()

        data = sorted(self.query_data(date), key=lambda x: datetime.strptime(x["start"], '%H:%M'))
        
        df = pd.DataFrame(data=data)

        df["date"] = date

        return df
    
    def show_availability(self, date, delta=[0,0]):
        if self.data is None: 
            self.load_data() 
        
        data = sorted(self.query_data(date), key=lambda x: datetime.strptime(x["start"], '%H:%M'))
        
        availability = []
    
        start = self.start_shift_time

        for appt in data: 

            end = datetime.strptime(appt["start"], '%H:%M')

            if (end - start).seconds != 0:

                new_time = {

                    "start": start.strftime("%H:%M"), 
                    "end": (start + (end - start)).strftime("%H:%M")

                           }

                availability.append(new_time)

            start = datetime.strptime(appt["end"], '%H:%M')           

        end = self.end_shift_time

        if (end - start).seconds != 0: 

            new_time = {

                    "start": start.strftime("%H:%M"), 
                    "end": (start + (end - start)).strftime("%H:%M")

                           }

        availability.append(new_time)

        return availability


# if __name__ == "__main__":
#     mycal = scheduler() 
#     # mycal.remove_appt("08:00", "08:30", "2022-11-16")
#     print(mycal.update_appt("08:00", "08:30", "08:00", "09:00", "2022-11-16")) 
