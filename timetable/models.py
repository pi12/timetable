# -*- coding: utf-8 -*-
from timetable import db

class Weekday(object):
    MONDAY    = 1
    TUESDAY   = 2
    WEDNESDAY = 3
    THURSDAY  = 4
    FRIDAY    = 5
    SATURDAY  = 6
    SUNDAY    = 7
    
    ALL = -1
    
    TITLE = ["Undefined", "Monday", "Thuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    NUMBER = {
        "monday"    : MONDAY,
        "thuesday"  : TUESDAY, 
        "wednesday" : WEDNESDAY, 
        "thursday"  : THURSDAY, 
        "friday"    : FRIDAY, 
        "saturday"  : SATURDAY, 
        "sunday"    : SUNDAY
        }
    
    @staticmethod
    def get_string(weekday):
        if weekday < 0 or weekday >= 8:
            return Weekday.TITLE[0]
        else:
            return Weekday.TITLE[weekday]

    @staticmethod
    def get_number(str_weekday):
        return Weekday.NUMBER.get(str_weekday.lower())
        
    @staticmethod
    def is_correct(weekday):
        if weekday < -1 or weekday >= 8:
            return False
        return True
    
class Week(object):
    UPPER = 0 # Верхняя (четная) неделя
    LOWER = 1 # Нижняя (нечетная) неделя
    BOTH  = 2 # Любая неделя
    
    TITLE = ["Upper", "Lower", "Both", "Undefined"]
    
    ALL = -1
    
    @staticmethod
    def get_string(week):
        if week < 0 or week > 2:
            return Week.TITLE[3]
        return Week.TITLE[week]
    
    @staticmethod
    def is_upper(week):
        return week == Week.UPPER
     
    @staticmethod
    def is_correct(week):
        if week < -1 or week > 2:
            return False
        return True

class SubgroupHelper(object):
    ALL     = 0b11111111
    FIRST   = 0b00000001
    SECOND  = 0b00000010
    THIRD   = 0b00000100
    FOURTH  = 0b00001000
    FIFTH   = 0b00010000
    SIXTH   = 0b00100000
    SEVENTH = 0b01000000
    EIGHTH  = 0b10000000
    
    MAX_COUNT = 8
    
    @staticmethod
    def get_numbers(bitmask):
        num = []
        for i in range(0, SubgroupHelper.MAX_COUNT):
            if (bitmask & (1 << i)) <> 0:
                num.append(i + 1)
        return num

class ItemNumberHelper(object):
    ALL = -1
    
    @staticmethod
    def is_correct(num):
        if num < -1 or num > 7:
            return False
        return True

class Lecturer(db.Document):
    name = db.StringField(max_length=100, required=True)                    # ФИО
    degree = db.StringField(max_length=100, default="Старший преподаватель")# Должность
    department = db.ReferenceField('Department', required=True)             # Кафедра
    lessons = db.ListField(db.ReferenceField('Lesson'))                     # Пары
    
class Faculty(db.Document):
    title = db.StringField(max_length=10, required=True)              # КНТ (название на русском)
    abbr = db.StringField(max_length=10, required=True, unique=True)  # cs (аббривиатура с англ. Computer science)
    description = db.StringField(max_length=500)                      # Описание факультета (полное название)
    departments = db.ListField(db.ReferenceField('Department'))       # Кафедры
    groups = db.ListField(db.ReferenceField('Group'))                 # Группы
    
class Department(db.Document):
    title = db.StringField(max_length=100, required=True)           # Название на русском
    abbr = db.StringField(max_length=10, required=True, unique=True)# pmi (аббривиатура с англ)
    description = db.StringField(max_length=500)                    # Описание кафедры
    lecturers = db.ListField(db.ReferenceField('Lecturer'))         # Преподаватели на кафедре

class Group(db.Document):
    title = db.StringField(max_length=10, required=True)              # ПИ-12а (название на русском)
    abbr = db.StringField(max_length=10, required=True, unique=True)  # pi (аббривиатура с англ)
    description = db.StringField(max_length=500)                      # Описание группы
    faculty = db.ReferenceField('Faculty', required=True)             # Факультет
    lessons = db.ListField(db.ReferenceField('Lesson'))               # Пары

class Subgroup(db.EmbeddedDocument):
    subgroup = db.IntField(min_value=0, max_value=256, required=True, default=256) # Подгруппа 0 - вся группа (0, 1, 2, 3, 4 ...)
    group = db.ReferenceField('Group', required=True)
    
class Lesson(db.Document):
    title = db.StringField(max_length=100, required=True)                   # Название предмета на русском
    room = db.StringField(max_length=10, required=True)                     # 8.705 (Номер аудитории)
    item_number = db.IntField(min_value=1, max_value=7, required=True)      # Номер пары (1, 2, 3, 4, 5)
    weekday = db.IntField(min_value=1, max_value=7, required=True)          # День недели (пн=1, вт=2, ср=3, ...)
    week = db.IntField(min_value=0, max_value=2, required=True, default=2)  # Неделя(верхняя=0, нижняя=1, любая=2)
    description = db.StringField(max_length=200)
    
    subgroups = db.ListField(db.EmbeddedDocumentField('Subgroup'), required=True)
    lecturer = db.ReferenceField('Lecturer', required=True)

Lecturer.register_delete_rule(Department, 'department', db.NULLIFY)    
Lecturer.register_delete_rule(Lesson, 'lessons', db.CASCADE)

Faculty.register_delete_rule(Department, 'departments', db.CASCADE)
Faculty.register_delete_rule(Group, 'groups', db.CASCADE)

Department.register_delete_rule(Lecturer, 'lecturers', db.CASCADE)

Group.register_delete_rule(Faculty, 'faculty', db.NULLIFY)
Group.register_delete_rule(Lesson, 'lessons', db.CASCADE)

Lesson.register_delete_rule(Lecturer, 'lecturer', db.NULLIFY)