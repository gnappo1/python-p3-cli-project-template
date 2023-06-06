from classes.__init__ import CURSOR, CONN
import re

class Appointment:
    def __init__(self, date, time, description, doctor_id, patient_id, id=None):
        self.date = date
        self.time = time
        self.description = description
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.id = id

    def __repr__(self):
        return (
            f"<Appointment {self.id}: {self.date} @{self.time}, "
            + f"{self.description}, "
            + f"Doctor ID: {self.doctor or self.doctor_id}, "
            + f"Patient ID: {self.patient or self.patient_id}>"
        )

    @property
    def doctor(self):
        CONN.execute(
        """
            SELECT * FROM doctors
            WHERE id = ?;
        """, (self.doctor_id,)
        )
        row = CURSOR.fetchone()
        return Doctor(row[1], row[2], row[3], row[0]) if row else None


    @doctor.setter
    def doctor(self, doctor_id):
        if isinstance(doctor_id, int) and doctor_id > 0 and Doctor.find_by_id(doctor_id):
            self._doctor_id = doctor_id
        else:
            raise ValueError("Doctor ID must be a positive integer and doctor must exist")

    @property
    def patient(self):
        CONN.execute(
        """
            SELECT * FROM patients
            WHERE id = ?;
        """, (self.patient_id,)
        )
        row = CURSOR.fetchone()
        return Patient(row[1], row[2], row[3], row[0]) if row else None


    @patient.setter
    def patient(self, patient_id):
        if isinstance(patient_id, int) and patient_id > 0 and Patient.find_by_id(patient_id):
            self._patient_id = patient_id

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        if re.match(r"([0][1-9]|[1][0-2])\/([0][1-9]|[12][0-9]|[3][01])\/\d{4}", date):
            self._date = date
        else:
            raise ValueError("Date must be in format MM/DD/YYYY")

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        if re.match(r"([0][0-9]|[1][0-2]):[0-5][0-9](AM|PM)", time):
            self._time = time
        else:
            raise ValueError("Time must be in format HH:MMAM or HH:MMPM")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str) and len(description) > 2:
            self._description = description
        else:
            raise ValueError("Description must be a string longer than 2 characters")

    def update(self):
        CURSOR.execute(
            """
            UPDATE appointments
            SET date = ?, time = ?, description = ?, doctor_id = ?, patient_id = ?
            WHERE id = ?
        """,
            (
                self.date,
                self.time,
                self.description,
                self.doctor_id,
                self.patient_id,
                self.id,
            ),
        )
        CONN.commit()
        return type(self).find_by_id(self.id)

    def save(self):
        # self is only instantiated so it has no id
        CURSOR.execute(
            """
            INSERT INTO appointments (date, time, description, doctor_id, patient_id)
            VALUES (?, ?, ?, ?, ?);
        """,
            (self.date, self.time, self.description, self.doctor_id, self.patient_id),
        )
        CONN.commit()
        self.id = CURSOR.lastrowid

    def delete(self):
        CURSOR.execute(
            """
            DELETE FROM appointments
            WHERE id = ?;
        """,
            (self.id,),
        )
        CONN.commit()

    @classmethod
    def create_table(cls):
        CONN.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                date TEXT,
                time TEXT,
                description TEXT,
                doctor_id INTEGER,
                patient_id INTEGER,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );
        """
        )
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute(
            """
            DROP TABLE IF EXISTS appointments;
        """
        )
        CONN.commit()

    @classmethod
    def create(cls, date, time, description, doctor_id, patient_id):
        # Initialize a new obj with the info provided
        new_appt = cls(date, time, description, doctor_id, patient_id)
        # save the obj to make sure it's in the db
        new_appt.save()
        return new_appt

    @classmethod
    def new_from_db(cls):
        CURSOR.execute(
            """
            SELECT * FROM appointments
            ORDER BY id DESC
            LIMIT 1;
        """
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[4], row[5], row[0])

    @classmethod
    def get_all(cls):
        CURSOR.execute(
            """
            SELECT * FROM appointments; 
        """
        )
        rows = CURSOR.fetchall()
        return [cls(row[1], row[2], row[3], row[4], row[5], row[0]) for row in rows]

    @classmethod
    def find_by_date_and_time(cls, date, time):
        CURSOR.execute(
            """
            SELECT * FROM appointments
            WHERE date is ? AND time is ?;
        """,
            (date, time),
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[4], row[5], row[0]) if row else None

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute(
            """
            SELECT * FROM appointments
            WHERE id is ?;
        """,
            (id,),
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[4], row[5], row[0]) if row else None

    @classmethod
    def find_or_create_by(cls, date, time, description, doctor_id, patient_id):
        cls.find_by_date_and_time(date, time) or cls.create(
            date, time, description, doctor_id, patient_id
        )


from classes.doctor import Doctor
from classes.patient import Patient
