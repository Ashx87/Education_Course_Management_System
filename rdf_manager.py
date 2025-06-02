from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
import pandas as pd
from typing import List, Dict, Any

class RDFDataManager:
    def __init__(self):
        self.graph = Graph()
        
        # 定义命名空间并正确绑定
        self.EDU = Namespace("http://example.org/education#")
        self.graph.bind("edu", self.EDU)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        
        # 初始化数据
        self.init_rdf_data()
    
    def init_rdf_data(self):
        """初始化RDF数据"""
        # 添加类定义
        self.graph.add((self.EDU.Person, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Student, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Student, RDFS.subClassOf, self.EDU.Person))
        self.graph.add((self.EDU.Instructor, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Instructor, RDFS.subClassOf, self.EDU.Person))
        self.graph.add((self.EDU.Course, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Department, RDF.type, RDFS.Class))
        
        # 添加属性定义
        self.graph.add((self.EDU.enrollsIn, RDF.type, RDF.Property))
        self.graph.add((self.EDU.teaches, RDF.type, RDF.Property))
        self.graph.add((self.EDU.hasPrerequisite, RDF.type, RDF.Property))
        self.graph.add((self.EDU.hasName, RDF.type, RDF.Property))
        self.graph.add((self.EDU.hasGPA, RDF.type, RDF.Property))
        self.graph.add((self.EDU.hasCredits, RDF.type, RDF.Property))
        
        # 添加示例数据
        self.add_sample_data()
    
    def add_sample_data(self):
        """添加示例数据"""
        # 部门数据
        cs_dept = self.EDU.ComputerScience
        self.graph.add((cs_dept, RDF.type, self.EDU.Department))
        self.graph.add((cs_dept, self.EDU.hasName, Literal("Computer Science")))
        
        # 课程数据
        courses_data = [
            {"uri": "CS101", "name": "Introduction to Programming", "credits": 3, "dept": cs_dept},
            {"uri": "CS201", "name": "Data Structures", "credits": 3, "dept": cs_dept},
            {"uri": "CS301", "name": "Algorithms", "credits": 3, "dept": cs_dept},
            {"uri": "CS401", "name": "Machine Learning", "credits": 4, "dept": cs_dept}
        ]
        
        for course in courses_data:
            course_uri = self.EDU[course["uri"]]
            self.graph.add((course_uri, RDF.type, self.EDU.Course))
            self.graph.add((course_uri, self.EDU.hasName, Literal(course["name"])))
            self.graph.add((course_uri, self.EDU.hasCredits, Literal(course["credits"])))
            self.graph.add((course_uri, self.EDU.belongsToDepartment, course["dept"]))
        
        # 先修课程关系
        self.graph.add((self.EDU.CS201, self.EDU.hasPrerequisite, self.EDU.CS101))
        self.graph.add((self.EDU.CS301, self.EDU.hasPrerequisite, self.EDU.CS201))
        self.graph.add((self.EDU.CS401, self.EDU.hasPrerequisite, self.EDU.CS301))
        
        # 教师数据
        instructors_data = [
            {"uri": "prof_smith", "name": "Dr. John Smith", "teaches": ["CS101", "CS201"]},
            {"uri": "prof_jones", "name": "Dr. Sarah Jones", "teaches": ["CS301", "CS401"]}
        ]
        
        for instructor in instructors_data:
            instructor_uri = self.EDU[instructor["uri"]]
            self.graph.add((instructor_uri, RDF.type, self.EDU.Instructor))
            self.graph.add((instructor_uri, self.EDU.hasName, Literal(instructor["name"])))
            for course_code in instructor["teaches"]:
                self.graph.add((instructor_uri, self.EDU.teaches, self.EDU[course_code]))
        
        # 学生数据
        students_data = [
            {"uri": "student_001", "name": "Alice Johnson", "id": "2021001", "gpa": 3.8, 
             "enrolls": ["CS101", "CS201"]},
            {"uri": "student_002", "name": "Bob Smith", "id": "2021002", "gpa": 3.5, 
             "enrolls": ["CS101"]},
            {"uri": "student_003", "name": "Carol Davis", "id": "2021003", "gpa": 3.9, 
             "enrolls": ["CS201", "CS301"]}
        ]
        
        for student in students_data:
            student_uri = self.EDU[student["uri"]]
            self.graph.add((student_uri, RDF.type, self.EDU.Student))
            self.graph.add((student_uri, self.EDU.hasName, Literal(student["name"])))
            self.graph.add((student_uri, self.EDU.hasStudentID, Literal(student["id"])))
            self.graph.add((student_uri, self.EDU.hasGPA, Literal(student["gpa"])))
            for course_code in student["enrolls"]:
                self.graph.add((student_uri, self.EDU.enrollsIn, self.EDU[course_code]))

class SPARQLQueryEngine:
    def __init__(self, rdf_manager: RDFDataManager):
        self.graph = rdf_manager.graph
        self.EDU = rdf_manager.EDU
    
    def query_all_students(self) -> pd.DataFrame:
        """查询所有学生信息"""
        query = """
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?student ?name ?studentId ?gpa
        WHERE {
            ?student rdf:type edu:Student .
            ?student edu:hasName ?name .
            ?student edu:hasStudentID ?studentId .
            ?student edu:hasGPA ?gpa .
        }
        ORDER BY ?name
        """
        
        try:
            results = self.graph.query(query)
            data = []
            for row in results:
                data.append({
                    'Student': str(row.student).split('#')[-1],
                    'Name': str(row.name),
                    'Student_ID': str(row.studentId),
                    'GPA': float(row.gpa)
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ 查询学生信息失败: {e}")
            return pd.DataFrame()
    
    def query_course_enrollments(self, course_code: str) -> pd.DataFrame:
        """查询特定课程的注册学生"""
        query = f"""
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?student ?name ?gpa
        WHERE {{
            ?student rdf:type edu:Student .
            ?student edu:hasName ?name .
            ?student edu:hasGPA ?gpa .
            ?student edu:enrollsIn edu:{course_code} .
        }}
        ORDER BY DESC(?gpa)
        """
        
        try:
            results = self.graph.query(query)
            data = []
            for row in results:
                data.append({
                    'Student': str(row.student).split('#')[-1],
                    'Name': str(row.name),
                    'GPA': float(row.gpa)
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ 查询课程注册信息失败: {e}")
            return pd.DataFrame()
    
    def query_prerequisites(self, course_code: str) -> List[str]:
        """查询课程的先修要求"""
        query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?prerequisite ?name
        WHERE {{
            edu:{course_code} edu:hasPrerequisite ?prerequisite .
            ?prerequisite edu:hasName ?name .
        }}
        """
        
        try:
            results = self.graph.query(query)
            prerequisites = []
            for row in results:
                prerequisites.append({
                    'code': str(row.prerequisite).split('#')[-1],
                    'name': str(row.name)
                })
            return prerequisites
        except Exception as e:
            print(f"❌ 查询先修要求失败: {e}")
            return []
    
    def query_student_recommendations(self, student_uri: str) -> pd.DataFrame:
        """为学生推荐课程"""
        query = f"""
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?course ?name ?credits
        WHERE {{
            ?course rdf:type edu:Course .
            ?course edu:hasName ?name .
            ?course edu:hasCredits ?credits .
            
            # 学生还没有注册这门课
            FILTER NOT EXISTS {{
                edu:{student_uri} edu:enrollsIn ?course .
            }}
            
            # 课程没有先修要求，或者学生已经完成先修要求
            FILTER NOT EXISTS {{
                ?course edu:hasPrerequisite ?prereq .
                FILTER NOT EXISTS {{
                    edu:{student_uri} edu:enrollsIn ?prereq .
                }}
            }}
        }}
        ORDER BY ?credits
        """
        
        try:
            results = self.graph.query(query)
            data = []
            for row in results:
                data.append({
                    'Course': str(row.course).split('#')[-1],
                    'Name': str(row.name),
                    'Credits': int(row.credits)
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ 查询推荐课程失败: {e}")
            return pd.DataFrame()
    
    def query_instructor_courses(self) -> pd.DataFrame:
        """查询教师授课情况"""
        query = """
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instructor ?instructorName ?course ?courseName
        WHERE {
            ?instructor rdf:type edu:Instructor .
            ?instructor edu:hasName ?instructorName .
            ?instructor edu:teaches ?course .
            ?course edu:hasName ?courseName .
        }
        ORDER BY ?instructorName
        """
        
        try:
            results = self.graph.query(query)
            data = []
            for row in results:
                data.append({
                    'Instructor': str(row.instructor).split('#')[-1],
                    'Instructor_Name': str(row.instructorName),
                    'Course': str(row.course).split('#')[-1],
                    'Course_Name': str(row.courseName)
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ 查询教师授课情况失败: {e}")
            return pd.DataFrame()
    
    def advanced_analytics_query(self) -> Dict[str, Any]:
        """高级分析查询 - 统计信息"""
        # 查询课程注册统计
        enrollment_query = """
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?course ?courseName (COUNT(?student) as ?enrollmentCount)
        WHERE {
            ?student edu:enrollsIn ?course .
            ?course edu:hasName ?courseName .
        }
        GROUP BY ?course ?courseName
        ORDER BY DESC(?enrollmentCount)
        """
        
        # 查询平均GPA
        gpa_query = """
        PREFIX edu: <http://example.org/education#>
        
        SELECT (AVG(?gpa) as ?avgGPA) (MAX(?gpa) as ?maxGPA) (MIN(?gpa) as ?minGPA)
        WHERE {
            ?student edu:hasGPA ?gpa .
        }
        """
        
        try:
            enrollment_results = self.graph.query(enrollment_query)
            gpa_results = list(self.graph.query(gpa_query))
            
            enrollment_data = []
            for row in enrollment_results:
                enrollment_data.append({
                    'Course': str(row.course).split('#')[-1],
                    'Course_Name': str(row.courseName),
                    'Enrollment': int(row.enrollmentCount)
                })
            
            gpa_stats = {}
            if gpa_results:
                gpa_result = gpa_results[0]
                gpa_stats = {
                    'average': float(gpa_result.avgGPA) if gpa_result.avgGPA else 0.0,
                    'maximum': float(gpa_result.maxGPA) if gpa_result.maxGPA else 0.0,
                    'minimum': float(gpa_result.minGPA) if gpa_result.minGPA else 0.0
                }
            
            return {
                'enrollment_stats': pd.DataFrame(enrollment_data),
                'gpa_stats': gpa_stats
            }
        except Exception as e:
            print(f"❌ 高级分析查询失败: {e}")
            return {
                'enrollment_stats': pd.DataFrame(),
                'gpa_stats': {'average': 0.0, 'maximum': 0.0, 'minimum': 0.0}
            }
    
    def load_external_rdf(self, file_path: str):
        """加载外部RDF文件"""
        try:
            self.graph.parse(file_path, format="xml")
            print(f"✅ 成功加载外部RDF文件: {file_path}")
            print(f"📊 当前图中包含 {len(self.graph)} 个三元组")
        except Exception as e:
            print(f"❌ 加载RDF文件失败: {e}")

# 使用示例
if __name__ == "__main__":
    print("🚀 初始化RDF数据管理器...")
    
    # 创建RDF数据管理器
    rdf_manager = RDFDataManager()
    
    # 尝试加载外部RDF文件
    try:
        rdf_manager.graph.parse("education_data.rdf", format="xml")
        print("✅ 成功加载 education_data.rdf")
    except Exception as e:
        print(f"⚠️ 无法加载外部RDF文件: {e}")
        print("使用内置示例数据")
    
    # 创建SPARQL查询引擎
    query_engine = SPARQLQueryEngine(rdf_manager)
    
    print(f"\n📊 数据统计: {len(rdf_manager.graph)} 个三元组")
    
    # 演示查询
    print("\n=== 演示查询 ===")
    
    print("\n👥 所有学生信息:")
    students = query_engine.query_all_students()
    if not students.empty:
        print(students.to_string(index=False))
    else:
        print("暂无学生数据")
    
    print("\n📚 CS101课程注册学生:")
    cs101_students = query_engine.query_course_enrollments("CS101")
    if not cs101_students.empty:
        print(cs101_students.to_string(index=False))
    else:
        print("暂无CS101注册数据")
    
    print("\n🔗 CS301先修要求:")
    prerequisites = query_engine.query_prerequisites("CS301")
    if prerequisites:
        for prereq in prerequisites:
            print(f"- {prereq['code']}: {prereq['name']}")
    else:
        print("CS301无先修要求或查询失败")
    
    print("\n🎯 为student_002推荐课程:")
    recommendations = query_engine.query_student_recommendations("student_002")
    if not recommendations.empty:
        print(recommendations.to_string(index=False))
    else:
        print("暂无推荐或查询失败")
    
    print("\n📈 高级分析:")
    analytics = query_engine.advanced_analytics_query()
    if not analytics['enrollment_stats'].empty:
        print("注册统计:")
        print(analytics['enrollment_stats'].to_string(index=False))
    
    if analytics['gpa_stats']['average'] > 0:
        print(f"\nGPA统计: {analytics['gpa_stats']}")
    
    # 保存RDF数据到文件
    try:
        rdf_manager.graph.serialize("education_data_output.rdf", format="xml")
        print("\n✅ RDF数据已保存到 education_data_output.rdf")
    except Exception as e:
        print(f"\n❌ 保存RDF文件失败: {e}")
    
    print("\n✅ RDF管理器测试完成！")