import mysql.connector
import numpy as np

class Parameters:
    
    def connect_database():
        db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="morbius", # change password
        auth_plugin='mysql_native_password'
        )
        db_cursor = db_connection.cursor(buffered=True)
        db_cursor.execute("USE earthquake")
        return db_cursor
    
    def num_of_immediate(db_cursor):
        db_cursor.execute("""SELECT COUNT(*) 
                        FROM VICTIM V, FIRSTAID F
                        WHERE V.victim_id = F.victim_id AND victim_condition = 3""")
        # # of immediate victims
        K = db_cursor.fetchall()[0][0]
        return K
    
    def num_of_delayed(db_cursor):
        db_cursor.execute("""SELECT COUNT(*) 
                     FROM VICTIM V, FIRSTAID F
                     WHERE V.victim_id = F.victim_id AND victim_condition = 2""")
        # # of delayed victims
        L = db_cursor.fetchall()[0][0]
        return L
            
    def num_of_hospitals(db_cursor):
        db_cursor.execute("""SELECT COUNT(*) 
                     FROM HOSPITAL_MASTER
                     WHERE is_operational = 1""")
        # # of delayed victims
        H = db_cursor.fetchall()[0][0]
        return H

    def victim_dict(db_cursor):
        db_cursor.execute("""SELECT V.victim_id, (victim_age_min+victim_age_max)/2, TIMESTAMPDIFF(MINUTE, MCI_datetime, applied_datetime), R.latitude, R.longitude, R.neighbourhood, victim_condition
                     FROM VICTIM V, MCI M, RESCUE R, FIRSTAID F
                     WHERE V.MCI_id = M.MCI_id AND V.victim_id = F.victim_id 
                     AND V.victim_id = R.victim_id AND (victim_condition = 2 OR victim_condition = 3)""")
        #victim: id, age, time passed, location, condition
        victim_info = db_cursor.fetchall()
        victim_dict = {}
        for row in victim_info:
            victim_dict[row[0]] = row[1:]
        return victim_dict
    
    def victim_id_lists(victim_dict):
        immediate_v_id = []
        delayed_v_id = []
        for key,value in victim_dict.items():
            if value[-1] == 3:
                immediate_v_id.append(key)
            else:
                delayed_v_id.append(key)
        return immediate_v_id, delayed_v_id
    
    def y_lists(victim_dict):
        y_immediate_list = []
        y_delayed_list = []
        for value in victim_dict.values():
            if value[-1] == 3:
                y_immediate_list.append(int(value[0]))
            else:
                y_delayed_list.append(int(value[0]))
        return y_immediate_list, y_delayed_list
        
    def t_lists(victim_dict):
        t_immediate_list = []
        t_delayed_list = []
        for value in victim_dict.values():
            if value[-1] == 3:
                t_immediate_list.append(int(value[1]))
            else:
                t_delayed_list.append(int(value[1]))
        return t_immediate_list, t_delayed_list
    
    def neighbourhood_lists(victim_dict):
        neighbourhood_immediate_list = []
        neighbourhood_delayed_list = []
        for value in victim_dict.values():
            if value[-1] == 3:
                neighbourhood_immediate_list.append(value[-2])
            else:
                neighbourhood_delayed_list.append(value[-2])
        return neighbourhood_immediate_list, neighbourhood_delayed_list
    
    def hospital_dict(db_cursor):
        db_cursor.execute("""SELECT hospital_id, latitude, longitude, bed_capacity
                     FROM HOSPITAL_MASTER
                     WHERE is_operational = 1""")
        #hospital: id, location, capacity
        hospital_info = db_cursor.fetchall()
        hospital_dict = {}
        for row in hospital_info:
            hospital_dict[row[0]] = row[1:]
        return hospital_dict
    
    def hospital_id_lists(hospital_dict):
        return list(hospital_dict.keys())
    
    def distances(db_cursor, victim_dict, hospital_dict):
        neighbourhood_locations = {}
        neighbourhood_list = []
        for value in victim_dict.values():
            neighbourhood_locations[value[4]] = value[2:4]
            if value[4] not in neighbourhood_list:
                neighbourhood_list.append(value[4])
        hospital_list = list(hospital_dict.keys())
        distances = np.ndarray(shape=(len(neighbourhood_list), len(hospital_list)))
        for key1, value1 in neighbourhood_locations.items():
            for key2, value2 in hospital_dict.items():
                neighbourhood = neighbourhood_list.index(key1)
                hospital_id = hospital_list.index(key2)
                latitude_diff = abs(value1[0] - value2[0])*100
                longitude_diff = abs(value1[0] - value2[0])*100
                distances[neighbourhood][hospital_id] = np.sqrt(latitude_diff**2 + longitude_diff**2)
        return neighbourhood_list, hospital_list, distances
    