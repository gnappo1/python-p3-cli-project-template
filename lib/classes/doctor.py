from classes.__init__ import CURSOR, CONN
import re


class Doctor:
    def __init__(self, full_name, phone_number, specialty, id=None):
        self.full_name = full_name
        self.phone_number = phone_number
        self.specialty = specialty
        self.id = id

    def __repr__(self):
        return f"<Doctor {self.id}: {self.full_name}, {self.phone_number}>"

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, full_name):
        if isinstance(full_name, str) and re.match(r"^[a-zA-Z]+ [a-zA-Z]+$", full_name):
            self._full_name = full_name
        else:
            raise ValueError(
                "Full name cannot be empty and must contain two words separated by a space"
            )

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, phone):
        if isinstance(phone, str) and re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
            self._phone = phone
        else:
            raise ValueError("Phone must be in format: 123-456-7890")

    def update(self):
        CURSOR.execute(
            """
            UPDATE doctors
            SET full_name = ?, phone_number = ?, specialty = ?
            WHERE id = ?
        """,
            (self.full_name, self.phone_number, self.specialty, self.id),
        )
        CONN.commit()
        return type(self).find_by_id(self.id)

    def save(self):
        # self is only instantiated so it has no id
        CURSOR.execute(
            """
            INSERT INTO doctors (full_name, phone_number, specialty)
            VALUES (?, ?, ?);
        """,
            (self.full_name, self.phone_number, self.specialty),
        )
        CONN.commit()
        self.id = CURSOR.lastrowid

    def delete(self):
        CURSOR.execute(
            """
            DELETE FROM doctors
            WHERE id = ?
        """,
            (self.id,),
        )
        CONN.commit()
        return self

    def appointments(self):
        CONN.execute(
            """
            SELECT * FROM appointments
            WHERE doctor_id = ?
        """,
            (self.id,),
        )
        rows = CURSOR.fetchall()
        return [
            Appointment(row[1], row[2], row[3], row[0]) for row in rows
        ]

    def patients(self):
        return list({appt.patient for appt in self.appointments()})

    @classmethod
    def create_table(cls):
        CONN.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone_number TEXT,
                specialty TEXT
            );
        """
        )
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute(
            """
            DROP TABLE IF EXISTS doctors;
        """
        )
        CONN.commit()

    @classmethod
    def create(cls, full_name, phone_number, specialty):
        # Initialize a new obj with the info provided
        new_appt = cls(full_name, phone_number, specialty)
        # save the obj to make sure it's in the db
        new_appt.save()
        return new_appt

    @classmethod
    def new_from_db(cls):
        CURSOR.execute(
            """
            SELECT * FROM doctors
            ORDER BY id DESC
            LIMIT 1;
        """
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[0])

    @classmethod
    def get_all(cls):
        CURSOR.execute(
            """
            SELECT * FROM doctors; 
        """
        )
        rows = CURSOR.fetchall()
        return [cls(row[1], row[2], row[3], row[0]) for row in rows]

    @classmethod
    def find_by_name(cls, name):
        CURSOR.execute(
        """
            SELECT * FROM doctors
            WHERE full_name is ?;
        """, (name, )
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[0]) if row else None

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute(
            """
            SELECT * FROM doctors
            WHERE id is ?;
        """,
            (id,),
        )
        row = CURSOR.fetchone()
        return cls(row[1], row[2], row[3], row[0]) if row else None

    @classmethod
    def find_or_create_by(cls, date, time, description, doctor, patient):
        cls.find_by_date_and_time(date, time) or cls.create(
            date, time, description, doctor, patient
        )


from classes.appointment import Appointment
