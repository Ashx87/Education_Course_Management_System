from owlready2 import *
import types

class EducationOntology:
    def __init__(self):
        self.onto = get_ontology("http://example.org/education.owl")
        self.create_classes()
        self.create_properties()
        self.create_individuals()
    
    def create_classes(self):
        with self.onto:
            # 主要类定义
            class Person(Thing): pass
            class Course(Thing): pass
            class Department(Thing): pass
            class Skill(Thing): pass
            class Assessment(Thing): pass
            
            # Person的子类
            class Student(Person): pass
            class Instructor(Person): pass
            class Administrator(Person): pass
            
            # Course的子类  
            class UndergraduateCourse(Course): pass
            class GraduateCourse(Course): pass
            class OnlineCourse(Course): pass
            class LabCourse(Course): pass
            
            # Assessment的子类
            class Exam(Assessment): pass
            class Assignment(Assessment): pass
            class Project(Assessment): pass
            
            # 课程难度等级
            class DifficultyLevel(Thing): pass
            class Beginner(DifficultyLevel): pass
            class Intermediate(DifficultyLevel): pass
            class Advanced(DifficultyLevel): pass
    
    def create_properties(self):
        with self.onto:
            # Object Properties (关系属性)
            class enrollsIn(ObjectProperty):
                domain = [self.onto.Student]
                range = [self.onto.Course]
            
            class teaches(ObjectProperty):
                domain = [self.onto.Instructor] 
                range = [self.onto.Course]
            
            class hasPrerequisite(ObjectProperty):
                domain = [self.onto.Course]
                range = [self.onto.Course]
            
            class belongsToDepartment(ObjectProperty):
                domain = [self.onto.Course]
                range = [self.onto.Department]
            
            class requiresSkill(ObjectProperty):
                domain = [self.onto.Course]
                range = [self.onto.Skill]
            
            class hasSkill(ObjectProperty):
                domain = [self.onto.Student]
                range = [self.onto.Skill]
            
            class hasAssessment(ObjectProperty):
                domain = [self.onto.Course]
                range = [self.onto.Assessment]
            
            class hasDifficulty(ObjectProperty):
                domain = [self.onto.Course]
                range = [self.onto.DifficultyLevel]
            
            # Data Properties (数据属性)
            class hasName(DataProperty):
                domain = [self.onto.Person, self.onto.Course, self.onto.Department]
                range = [str]
            
            class hasStudentID(DataProperty):
                domain = [self.onto.Student]
                range = [str]
            
            class hasCourseCode(DataProperty):
                domain = [self.onto.Course]
                range = [str]
            
            class hasCredits(DataProperty):
                domain = [self.onto.Course]
                range = [int]
            
            class hasGPA(DataProperty):
                domain = [self.onto.Student]
                range = [float]
            
            class hasCapacity(DataProperty):
                domain = [self.onto.Course]
                range = [int]
            
            class hasDuration(DataProperty):
                domain = [self.onto.Course]
                range = [int]  # 以小时为单位
    
    def create_individuals(self):
        with self.onto:
            # 创建院系
            cs_dept = self.onto.Department("Computer_Science")
            cs_dept.hasName = ["Computer Science"]
            
            math_dept = self.onto.Department("Mathematics") 
            math_dept.hasName = ["Mathematics"]
            
            # 创建技能
            programming = self.onto.Skill("Programming")
            algorithms = self.onto.Skill("Algorithms")
            databases = self.onto.Skill("Databases")
            math_analysis = self.onto.Skill("Mathematical_Analysis")
            
            # 创建难度等级实例
            beginner = self.onto.Beginner("Beginner_Level")
            intermediate = self.onto.Intermediate("Intermediate_Level") 
            advanced = self.onto.Advanced("Advanced_Level")
            
            # 创建课程示例
            intro_prog = self.onto.UndergraduateCourse("CS101")
            intro_prog.hasName = ["Introduction to Programming"]
            intro_prog.hasCourseCode = ["CS101"]
            intro_prog.hasCredits = [3]
            intro_prog.hasCapacity = [30]
            intro_prog.hasDuration = [48]
            intro_prog.belongsToDepartment = [cs_dept]
            intro_prog.requiresSkill = [programming]
            intro_prog.hasDifficulty = [beginner]
            
            data_structures = self.onto.UndergraduateCourse("CS201")
            data_structures.hasName = ["Data Structures"]
            data_structures.hasCourseCode = ["CS201"]
            data_structures.hasCredits = [3]
            data_structures.hasCapacity = [25]
            data_structures.hasDuration = [48]
            data_structures.belongsToDepartment = [cs_dept]
            data_structures.requiresSkill = [programming, algorithms]
            data_structures.hasDifficulty = [intermediate]
            data_structures.hasPrerequisite = [intro_prog]
            
            # 创建教师
            prof_smith = self.onto.Instructor("Prof_Smith")
            prof_smith.hasName = ["Dr. John Smith"]
            prof_smith.teaches = [intro_prog, data_structures]
            
            # 创建学生示例
            student1 = self.onto.Student("Student_001")
            student1.hasName = ["Alice Johnson"]
            student1.hasStudentID = ["2021001"]
            student1.hasGPA = [3.8]
            student1.hasSkill = [programming]
            student1.enrollsIn = [intro_prog]
    
    def save_ontology(self, filename="education.owl"):
        """保存本体到文件"""
        self.onto.save(file=filename, format="rdfxml")
        print(f"Ontology saved to {filename}")
    
    def get_ontology(self):
        return self.onto

# 使用示例
if __name__ == "__main__":
    # 创建教育本体
    edu_onto = EducationOntology()
    edu_onto.save_ontology()
    
    # 运行推理引擎
    sync_reasoner_pellet()
    
    print("教育本体创建完成！")
    print(f"类的数量: {len(list(edu_onto.onto.classes()))}")
    print(f"属性的数量: {len(list(edu_onto.onto.properties()))}")
    print(f"个体的数量: {len(list(edu_onto.onto.individuals()))}")