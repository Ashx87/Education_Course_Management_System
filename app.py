from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import io
import base64
import networkx as nx
import os

# 导入自定义模块
try:
    from education_ontology import EducationOntology
    from rdf_manager import RDFDataManager, SPARQLQueryEngine
    from inference_engine import EducationInferenceEngine
    print("✅ 成功导入所有模块")
except ImportError as e:
    print(f"⚠️ 模块导入失败: {e}")
    print("将使用简化版本运行")

app = Flask(__name__)

# 全局变量用于存储系统组件
rdf_manager = None
query_engine = None
inference_engine = None

def initialize_system():
    """初始化系统组件"""
    global rdf_manager, query_engine, inference_engine
    
    try:
        print("🚀 正在初始化教育管理系统...")
        
        # 初始化RDF数据管理器
        rdf_manager = RDFDataManager()
        
        # 尝试加载外部RDF数据
        if os.path.exists("education_data.rdf"):
            try:
                rdf_manager.load_external_rdf("education_data.rdf")
            except Exception as e:
                print(f"⚠️ 加载外部RDF数据失败: {e}")
        
        # 初始化查询引擎
        query_engine = SPARQLQueryEngine(rdf_manager)
        
        # 初始化推理引擎
        owl_file = "education.owl" if os.path.exists("education.owl") else None
        rdf_file = "education_data.rdf" if os.path.exists("education_data.rdf") else None
        inference_engine = EducationInferenceEngine(owl_file, rdf_file)
        
        print("✅ 系统初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return False

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/students')
def students():
    """学生列表页面"""
    try:
        if query_engine:
            students_df = query_engine.query_all_students()
            students_data = students_df.to_dict('records') if not students_df.empty else []
        else:
            students_data = []
        
        # 如果没有数据，提供示例数据
        if not students_data:
            students_data = [
                {'Student': 'student_001', 'Name': 'Alice Johnson', 'Student_ID': '2021001', 'GPA': 3.8},
                {'Student': 'student_002', 'Name': 'Bob Smith', 'Student_ID': '2021002', 'GPA': 3.5},
                {'Student': 'student_003', 'Name': 'Carol Davis', 'Student_ID': '2021003', 'GPA': 3.9}
            ]
        
        return render_template('students.html', students=students_data)
    except Exception as e:
        print(f"❌ 学生页面错误: {e}")
        return render_template('students.html', students=[])

@app.route('/courses')
def courses():
    """课程列表页面"""
    try:
        if query_engine:
            # 获取所有课程信息
            query = """
            PREFIX edu: <http://example.org/education#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            SELECT ?course ?name ?credits WHERE {
                ?course rdf:type edu:Course .
                ?course edu:hasName ?name .
                ?course edu:hasCredits ?credits .
            }
            ORDER BY ?course
            """
            
            results = query_engine.graph.query(query)
            courses_data = []
            for row in results:
                courses_data.append({
                    'code': str(row.course).split('#')[-1],
                    'name': str(row.name),
                    'credits': int(row.credits)
                })
        else:
            courses_data = []
        
        # 如果没有数据，提供示例数据
        if not courses_data:
            courses_data = [
                {'code': 'CS101', 'name': 'Introduction to Programming', 'credits': 3},
                {'code': 'CS201', 'name': 'Data Structures', 'credits': 3},
                {'code': 'CS301', 'name': 'Database Systems', 'credits': 3},
                {'code': 'CS401', 'name': 'Machine Learning', 'credits': 4}
            ]
        
        return render_template('courses.html', courses=courses_data)
    except Exception as e:
        print(f"❌ 课程页面错误: {e}")
        return render_template('courses.html', courses=[])

@app.route('/course/<course_code>')
def course_detail(course_code):
    """课程详情页面"""
    try:
        # 获取课程基本信息
        course_info = {'code': course_code, 'name': f'Course {course_code}', 'credits': 3}
        enrollments = []
        prerequisites = []
        instructors = []
        
        if query_engine:
            # 获取课程信息
            course_query = f"""
            PREFIX edu: <http://example.org/education#>
            
            SELECT ?name ?credits WHERE {{
                edu:{course_code} edu:hasName ?name .
                edu:{course_code} edu:hasCredits ?credits .
            }}
            """
            
            try:
                for row in query_engine.graph.query(course_query):
                    course_info = {
                        'code': course_code,
                        'name': str(row.name),
                        'credits': int(row.credits)
                    }
                    break
            except:
                pass
            
            # 获取注册学生
            try:
                enrollments_df = query_engine.query_course_enrollments(course_code)
                enrollments = enrollments_df.to_dict('records') if not enrollments_df.empty else []
            except:
                pass
            
            # 获取先修要求
            try:
                prerequisites = query_engine.query_prerequisites(course_code)
            except:
                pass
            
            # 获取授课教师
            instructor_query = f"""
            PREFIX edu: <http://example.org/education#>
            
            SELECT ?instructor ?name WHERE {{
                ?instructor edu:teaches edu:{course_code} .
                ?instructor edu:hasName ?name .
            }}
            """
            
            try:
                for row in query_engine.graph.query(instructor_query):
                    instructors.append({
                        'id': str(row.instructor).split('#')[-1],
                        'name': str(row.name)
                    })
            except:
                pass
        
        return render_template('course_detail.html', 
                             course=course_info, 
                             enrollments=enrollments,
                             prerequisites=prerequisites,
                             instructors=instructors)
    except Exception as e:
        print(f"❌ 课程详情页面错误: {e}")
        return redirect(url_for('courses'))

@app.route('/student/<student_id>')
def student_detail(student_id):
    """学生详情页面"""
    try:
        if inference_engine:
            analysis = inference_engine.analyze_student_performance(student_id)
        else:
            # 提供默认分析结果
            analysis = {
                'student_info': {'name': f'Student {student_id}', 'gpa': 3.0, 'student_id': student_id},
                'enrolled_courses': [],
                'total_credits': 0,
                'performance_level': 'Good',
                'suggestions': ['继续保持学习状态'],
                'next_recommendations': []
            }
        
        return render_template('student_detail.html', analysis=analysis)
    except Exception as e:
        print(f"❌ 学生详情页面错误: {e}")
        return redirect(url_for('students'))

@app.route('/recommendations/<student_id>')
def recommendations(student_id):
    """学生课程推荐页面"""
    try:
        # 获取推荐课程
        if inference_engine:
            recommendations_list = inference_engine.recommend_next_courses(student_id, 10)
        else:
            recommendations_list = []
        
        # 获取学生基本信息
        student_info = {'id': student_id, 'name': f'Student {student_id}', 'gpa': 3.0}
        
        if query_engine:
            student_query = f"""
            PREFIX edu: <http://example.org/education#>
            
            SELECT ?name ?gpa WHERE {{
                edu:{student_id} edu:hasName ?name .
                edu:{student_id} edu:hasGPA ?gpa .
            }}
            """
            
            try:
                for row in query_engine.graph.query(student_query):
                    student_info = {
                        'id': student_id,
                        'name': str(row.name),
                        'gpa': float(row.gpa)
                    }
                    break
            except:
                pass
        
        return render_template('recommendations.html', 
                             student=student_info, 
                             recommendations=recommendations_list)
    except Exception as e:
        print(f"❌ 推荐页面错误: {e}")
        return redirect(url_for('students'))

@app.route('/analytics')
def analytics():
    """分析统计页面"""
    try:
        # 获取高级分析数据
        if query_engine:
            analytics_data = query_engine.advanced_analytics_query()
        else:
            analytics_data = {
                'enrollment_stats': pd.DataFrame(),
                'gpa_stats': {'average': 0.0, 'maximum': 0.0, 'minimum': 0.0}
            }
        
        # 生成图表
        enrollment_chart = create_enrollment_chart(analytics_data['enrollment_stats'])
        gpa_distribution_chart = create_gpa_distribution_chart()
        
        enrollment_stats = analytics_data['enrollment_stats'].to_dict('records') if not analytics_data['enrollment_stats'].empty else []
        
        return render_template('analytics.html', 
                             enrollment_stats=enrollment_stats,
                             gpa_stats=analytics_data['gpa_stats'],
                             enrollment_chart=enrollment_chart,
                             gpa_chart=gpa_distribution_chart)
    except Exception as e:
        print(f"❌ 分析页面错误: {e}")
        return render_template('analytics.html', 
                             enrollment_stats=[],
                             gpa_stats={'average': 0.0, 'maximum': 0.0, 'minimum': 0.0},
                             enrollment_chart="",
                             gpa_chart="")

@app.route('/api/student/<student_id>/check_prerequisite/<course_code>')
def api_check_prerequisite(student_id, course_code):
    """API: 检查学生先修要求"""
    try:
        if inference_engine:
            result = inference_engine.check_prerequisite_completion(student_id, course_code)
        else:
            result = {
                'can_enroll': True,
                'missing_prerequisites': [],
                'completed_courses': [],
                'required_prerequisites': []
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/course_graph')
def api_course_graph():
    """API: 获取课程依赖关系图数据"""
    try:
        if inference_engine:
            graph = inference_engine.course_graph
            
            nodes = []
            edges = []
            
            for node in graph.nodes():
                nodes.append({'id': node, 'label': node})
            
            for edge in graph.edges():
                edges.append({'from': edge[0], 'to': edge[1]})
            
            return jsonify({'nodes': nodes, 'edges': edges})
        else:
            return jsonify({'nodes': [], 'edges': []})
    except Exception as e:
        return jsonify({'error': str(e)})

def create_enrollment_chart(enrollment_df):
    """创建注册统计图表"""
    try:
        if enrollment_df.empty:
            # 创建示例数据
            enrollment_df = pd.DataFrame({
                'Course': ['CS101', 'CS201', 'CS301'],
                'Enrollment': [15, 12, 8]
            })
        
        plt.figure(figsize=(10, 6))
        plt.bar(enrollment_df['Course'], enrollment_df['Enrollment'])
        plt.title('Course Enrollment Statistics')
        plt.xlabel('Course')
        plt.ylabel('Number of Students')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 转换为base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return chart_url
    except Exception as e:
        print(f"❌ 创建注册图表失败: {e}")
        return ""

def create_gpa_distribution_chart():
    """创建GPA分布图表"""
    try:
        if query_engine:
            students_df = query_engine.query_all_students()
        else:
            students_df = pd.DataFrame()
        
        if students_df.empty:
            # 创建示例数据
            gpas = [3.8, 3.5, 3.9, 3.2, 3.6, 3.4, 3.7, 3.3]
        else:
            gpas = students_df['GPA'].tolist()
        
        plt.figure(figsize=(8, 6))
        plt.hist(gpas, bins=10, edgecolor='black', alpha=0.7)
        plt.title('GPA Distribution')
        plt.xlabel('GPA')
        plt.ylabel('Number of Students')
        plt.grid(True, alpha=0.3)
        
        # 转换为base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return chart_url
    except Exception as e:
        print(f"❌ 创建GPA图表失败: {e}")
        return ""

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# 在应用启动时初始化系统
@app.before_request
def before_first_request():
    initialize_system()

if __name__ == '__main__':
    print("🎓 启动教育课程管理系统...")
    
    # 手动初始化系统（用于开发模式）
    success = initialize_system()
    
    if success:
        print("✅ 系统准备就绪！")
        print("🌐 访问地址: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("⚠️ 系统部分功能可能不可用，但仍将启动Web服务")
        print("🌐 访问地址: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)