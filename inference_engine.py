from owlready2 import *
from rdflib import Graph, Namespace, RDF, RDFS
import networkx as nx
from typing import List, Dict, Tuple, Any
import pandas as pd

class EducationInferenceEngine:
    def __init__(self, ontology_file="education.owl", rdf_file="education_data.rdf"):
        # 创建知识图谱
        self.graph = Graph()
        
        # 定义命名空间并绑定到图中
        self.EDU = Namespace("http://example.org/education#")
        self.graph.bind("edu", self.EDU)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        
        # 加载RDF数据
        if rdf_file:
            try:
                self.graph.parse(rdf_file, format="xml")
                print(f"✅ 成功加载RDF数据: {len(self.graph)} 个三元组")
            except Exception as e:
                print(f"❌ 加载RDF文件失败: {e}")
                # 如果加载失败，创建一些基础数据
                self.create_sample_data()
        
        # 尝试加载本体（如果文件存在）
        try:
            if ontology_file and ontology_file.endswith('.owl'):
                self.onto = get_ontology(f"file://{ontology_file}").load()
                print(f"✅ 成功加载OWL本体")
            else:
                self.onto = None
        except Exception as e:
            print(f"⚠️ 加载OWL本体失败: {e}")
            self.onto = None
        
        # 创建课程依赖图
        self.course_graph = self.build_course_dependency_graph()
        
    def create_sample_data(self):
        """如果RDF文件加载失败，创建一些基础示例数据"""
        print("🔧 创建基础示例数据...")
        
        # 添加基础类型定义
        self.graph.add((self.EDU.Course, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Student, RDF.type, RDFS.Class))
        self.graph.add((self.EDU.Instructor, RDF.type, RDFS.Class))
        
        # 添加示例课程
        courses = [
            ("CS101", "Introduction to Programming", 3),
            ("CS201", "Data Structures", 3),
            ("CS301", "Database Systems", 3),
            ("MATH101", "Calculus I", 4)
        ]
        
        for code, name, credits in courses:
            course_uri = self.EDU[code]
            self.graph.add((course_uri, RDF.type, self.EDU.Course))
            self.graph.add((course_uri, self.EDU.hasName, rdflib.Literal(name)))
            self.graph.add((course_uri, self.EDU.hasCourseCode, rdflib.Literal(code)))
            self.graph.add((course_uri, self.EDU.hasCredits, rdflib.Literal(credits)))
        
        # 添加先修关系
        self.graph.add((self.EDU.CS201, self.EDU.hasPrerequisite, self.EDU.CS101))
        self.graph.add((self.EDU.CS301, self.EDU.hasPrerequisite, self.EDU.CS201))
        
        print(f"✅ 创建了 {len(self.graph)} 个基础三元组")
        
    def build_course_dependency_graph(self) -> nx.DiGraph:
        """构建课程依赖关系图"""
        G = nx.DiGraph()
        
        # 修复：使用正确的SPARQL查询语法
        # 从RDF数据中提取课程和先修关系
        prereq_query = """
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?course ?prerequisite WHERE {
            ?course edu:hasPrerequisite ?prerequisite .
        }
        """
        
        # 添加所有课程作为节点
        all_courses_query = """
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?course WHERE {
            ?course rdf:type edu:Course .
        }
        """
        
        try:
            # 添加所有课程节点
            for row in self.graph.query(all_courses_query):
                course_code = str(row.course).split('#')[-1]
                G.add_node(course_code)
            
            # 添加先修关系边
            for row in self.graph.query(prereq_query):
                course = str(row.course).split('#')[-1]
                prereq = str(row.prerequisite).split('#')[-1]
                G.add_edge(prereq, course)  # 从先修课程指向后续课程
            
            print(f"✅ 构建课程依赖图: {len(G.nodes())} 个课程, {len(G.edges())} 个依赖关系")
            
        except Exception as e:
            print(f"⚠️ 构建课程图时出错: {e}")
            # 如果查询失败，创建一个基础图
            G.add_nodes_from(["CS101", "CS201", "CS301", "MATH101"])
            G.add_edge("CS101", "CS201")
            G.add_edge("CS201", "CS301")
        
        return G
    
    def infer_course_sequence(self, target_course: str) -> List[str]:
        """推断到达目标课程的学习路径"""
        try:
            # 找到所有到目标课程的路径
            paths = []
            for node in self.course_graph.nodes():
                if nx.has_path(self.course_graph, node, target_course):
                    try:
                        path = nx.shortest_path(self.course_graph, node, target_course)
                        if len(path) > 1:  # 确保不是自己到自己
                            paths.append(path)
                    except nx.NetworkXNoPath:
                        continue
            
            # 返回最短的完整路径
            if paths:
                return min(paths, key=len)
            else:
                return [target_course]
        except:
            return [target_course]
    
    def check_prerequisite_completion(self, student_id: str, course_code: str) -> Dict[str, Any]:
        """检查学生是否满足课程先修要求"""
        # 获取学生已完成的课程
        completed_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?course WHERE {{
            edu:{student_id} edu:enrollsIn ?course .
        }}
        """
        
        completed_courses = set()
        try:
            for row in self.graph.query(completed_query):
                completed_courses.add(str(row.course).split('#')[-1])
        except Exception as e:
            print(f"⚠️ 查询学生课程失败: {e}")
        
        # 获取目标课程的先修要求
        prereq_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?prerequisite WHERE {{
            edu:{course_code} edu:hasPrerequisite ?prerequisite .
        }}
        """
        
        required_prereqs = set()
        try:
            for row in self.graph.query(prereq_query):
                required_prereqs.add(str(row.prerequisite).split('#')[-1])
        except Exception as e:
            print(f"⚠️ 查询先修要求失败: {e}")
        
        # 检查是否满足要求
        missing_prereqs = required_prereqs - completed_courses
        
        return {
            'can_enroll': len(missing_prereqs) == 0,
            'missing_prerequisites': list(missing_prereqs),
            'completed_courses': list(completed_courses),
            'required_prerequisites': list(required_prereqs)
        }
    
    def recommend_next_courses(self, student_id: str, max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """为学生推荐下一步可以学习的课程"""
        # 获取学生信息
        student_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?gpa WHERE {{
            edu:{student_id} edu:hasGPA ?gpa .
        }}
        """
        
        student_gpa = 3.0  # 默认GPA
        try:
            for row in self.graph.query(student_query):
                student_gpa = float(row.gpa)
                break
        except Exception as e:
            print(f"⚠️ 查询学生GPA失败: {e}")
        
        # 获取学生已完成的课程
        completed_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?course WHERE {{
            edu:{student_id} edu:enrollsIn ?course .
        }}
        """
        
        completed_courses = set()
        try:
            for row in self.graph.query(completed_query):
                completed_courses.add(str(row.course).split('#')[-1])
        except Exception as e:
            print(f"⚠️ 查询已完成课程失败: {e}")
        
        # 获取所有可用课程
        all_courses_query = """
        PREFIX edu: <http://example.org/education#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?course ?name ?credits WHERE {
            ?course rdf:type edu:Course .
            ?course edu:hasName ?name .
            ?course edu:hasCredits ?credits .
        }
        """
        
        recommendations = []
        
        try:
            for row in self.graph.query(all_courses_query):
                course_code = str(row.course).split('#')[-1]
                course_name = str(row.name)
                credits = int(row.credits)
                
                # 跳过已完成的课程
                if course_code in completed_courses:
                    continue
                
                # 检查先修要求
                prereq_check = self.check_prerequisite_completion(student_id, course_code)
                
                if prereq_check['can_enroll']:
                    # 计算推荐分数
                    score = self.calculate_recommendation_score(
                        student_gpa, course_code, completed_courses
                    )
                    
                    recommendations.append({
                        'course_code': course_code,
                        'course_name': course_name,
                        'credits': credits,
                        'recommendation_score': score,
                        'learning_path': self.infer_course_sequence(course_code)
                    })
        except Exception as e:
            print(f"⚠️ 生成推荐失败: {e}")
            # 返回基础推荐
            recommendations = [
                {
                    'course_code': 'CS101',
                    'course_name': 'Introduction to Programming',
                    'credits': 3,
                    'recommendation_score': 75.0,
                    'learning_path': ['CS101']
                }
            ]
        
        # 按推荐分数排序
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations[:max_recommendations]
    
    def calculate_recommendation_score(self, student_gpa: float, course_code: str, 
                                     completed_courses: set) -> float:
        """计算课程推荐分数"""
        base_score = 50.0
        
        # GPA因子 - 高GPA学生推荐更有挑战性的课程
        gpa_factor = min(student_gpa / 4.0, 1.0)  # 限制在1.0以内
        
        # 课程级别因子
        if course_code.endswith('01'):  # 入门课程 (如CS101)
            level_factor = 0.8
        elif course_code.endswith('01'):  # 中级课程 (如CS201)
            level_factor = 1.0
        else:  # 高级课程
            level_factor = 1.2
        
        # 先修课程完成度因子
        prereq_completion = min(len(completed_courses) / 10.0, 1.0)  # 假设平均需要10门课程
        
        # 计算最终分数
        score = base_score * gpa_factor * level_factor * (1 + prereq_completion)
        
        return min(score, 100.0)  # 限制最高分数为100
    
    def analyze_student_performance(self, student_id: str) -> Dict[str, Any]:
        """分析学生学习表现"""
        # 获取学生基本信息
        student_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?name ?gpa ?studentId WHERE {{
            edu:{student_id} edu:hasName ?name .
            edu:{student_id} edu:hasGPA ?gpa .
            edu:{student_id} edu:hasStudentID ?studentId .
        }}
        """
        
        student_info = {}
        try:
            for row in self.graph.query(student_query):
                student_info = {
                    'name': str(row.name),
                    'gpa': float(row.gpa),
                    'student_id': str(row.studentId)
                }
                break
        except Exception as e:
            print(f"⚠️ 查询学生信息失败: {e}")
            student_info = {
                'name': f'Student {student_id}',
                'gpa': 3.0,
                'student_id': student_id
            }
        
        # 获取已注册课程
        enrolled_query = f"""
        PREFIX edu: <http://example.org/education#>
        
        SELECT ?course ?name ?credits WHERE {{
            edu:{student_id} edu:enrollsIn ?course .
            ?course edu:hasName ?name .
            ?course edu:hasCredits ?credits .
        }}
        """
        
        enrolled_courses = []
        total_credits = 0
        
        try:
            for row in self.graph.query(enrolled_query):
                course_info = {
                    'code': str(row.course).split('#')[-1],
                    'name': str(row.name),
                    'credits': int(row.credits)
                }
                enrolled_courses.append(course_info)
                total_credits += course_info['credits']
        except Exception as e:
            print(f"⚠️ 查询注册课程失败: {e}")
        
        # 性能评估
        performance_level = self.assess_performance_level(student_info['gpa'])
        
        # 生成建议
        suggestions = self.generate_academic_suggestions(
            student_info['gpa'], len(enrolled_courses), total_credits
        )
        
        return {
            'student_info': student_info,
            'enrolled_courses': enrolled_courses,
            'total_credits': total_credits,
            'performance_level': performance_level,
            'suggestions': suggestions,
            'next_recommendations': self.recommend_next_courses(student_id, 3)
        }
    
    def assess_performance_level(self, gpa: float) -> str:
        """评估学生表现水平"""
        if gpa >= 3.7:
            return "Excellent"
        elif gpa >= 3.3:
            return "Good"
        elif gpa >= 3.0:
            return "Satisfactory"
        elif gpa >= 2.5:
            return "Needs Improvement"
        else:
            return "At Risk"
    
    def generate_academic_suggestions(self, gpa: float, course_count: int, 
                                    total_credits: int) -> List[str]:
        """生成学术建议"""
        suggestions = []
        
        if gpa < 3.0:
            suggestions.append("建议寻求学术辅导以提高GPA")
            suggestions.append("考虑减少课程负荷，专注于基础课程")
        
        if course_count < 4:
            suggestions.append("可以考虑增加课程负荷以加快学习进度")
        
        if total_credits > 18:
            suggestions.append("当前学分负荷较重，注意学习与生活平衡")
        
        if gpa >= 3.5:
            suggestions.append("表现优秀！可以考虑挑战更高难度的课程")
            suggestions.append("建议参与研究项目或实习机会")
        
        if not suggestions:
            suggestions.append("继续保持当前的学习状态")
        
        return suggestions
    
    def export_analysis_report(self, student_id: str, filename: str = None) -> str:
        """导出学生分析报告"""
        analysis = self.analyze_student_performance(student_id)
        
        if filename is None:
            filename = f"student_analysis_{student_id}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== 学生学习分析报告 ===\n\n")
                f.write(f"学生姓名: {analysis['student_info']['name']}\n")
                f.write(f"学号: {analysis['student_info']['student_id']}\n")
                f.write(f"当前GPA: {analysis['student_info']['gpa']}\n")
                f.write(f"表现水平: {analysis['performance_level']}\n")
                f.write(f"总学分: {analysis['total_credits']}\n\n")
                
                f.write("=== 已注册课程 ===\n")
                for course in analysis['enrolled_courses']:
                    f.write(f"- {course['code']}: {course['name']} ({course['credits']}学分)\n")
                
                f.write("\n=== 学术建议 ===\n")
                for suggestion in analysis['suggestions']:
                    f.write(f"- {suggestion}\n")
                
                f.write("\n=== 推荐课程 ===\n")
                for rec in analysis['next_recommendations']:
                    f.write(f"- {rec['course_code']}: {rec['course_name']} ")
                    f.write(f"(推荐分数: {rec['recommendation_score']:.1f})\n")
            
            print(f"✅ 报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
        
        return filename

# 使用示例
if __name__ == "__main__":
    print("🚀 初始化教育推理引擎...")
    
    # 创建推理引擎
    try:
        engine = EducationInferenceEngine()
        
        print("\n=== 测试推理功能 ===")
        
        # 为学生推荐课程
        print("\n🎯 为student_002推荐课程:")
        recommendations = engine.recommend_next_courses("student_002")
        for rec in recommendations:
            print(f"课程: {rec['course_code']} - {rec['course_name']}")
            print(f"推荐分数: {rec['recommendation_score']:.1f}")
            print(f"学习路径: {' -> '.join(rec['learning_path'])}")
            print("-" * 40)
        
        # 分析学生表现
        print("\n📊 学生表现分析:")
        analysis = engine.analyze_student_performance("student_001")
        print(f"学生: {analysis['student_info']['name']}")
        print(f"表现水平: {analysis['performance_level']}")
        print(f"学术建议: {analysis['suggestions'][:2]}")  # 显示前两个建议
        
        # 检查先修要求
        print("\n🔍 先修要求检查:")
        prereq_check = engine.check_prerequisite_completion("student_002", "CS201")
        print(f"可以注册CS201: {prereq_check['can_enroll']}")
        if prereq_check['missing_prerequisites']:
            print(f"缺少先修课程: {prereq_check['missing_prerequisites']}")
        
        print("\n✅ 推理引擎测试完成！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("请确保 education_data.rdf 文件存在且格式正确")