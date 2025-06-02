import os

# HTML模板内容
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Education Management System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        .sidebar {
            height: 100vh;
            background-color: #f8f9fa;
            padding: 20px;
        }
        .main-content {
            padding: 20px;
        }
        .card {
            margin-bottom: 20px;
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">🎓 Education Management System</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/students">Students</a>
                <a class="nav-link" href="/courses">Courses</a>
                <a class="nav-link" href="/analytics">Analytics</a>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar">
                <h5>Navigation</h5>
                <ul class="nav nav-pills flex-column">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/students">Students</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/courses">Courses</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/analytics">Analytics</a>
                    </li>
                </ul>
            </div>
            
            <div class="col-md-10 main-content">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Dashboard - Education Management System{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>📊 Education Management Dashboard</h1>
        <p class="lead">基于语义网技术的智能教育课程管理系统</p>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">👥 学生管理</h5>
                <p class="card-text">查看学生信息、学习进度和个性化推荐</p>
                <a href="/students" class="btn btn-primary">查看学生</a>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">📚 课程管理</h5>
                <p class="card-text">管理课程信息、先修要求和注册情况</p>
                <a href="/courses" class="btn btn-primary">查看课程</a>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">📈 数据分析</h5>
                <p class="card-text">查看统计数据和可视化分析报告</p>
                <a href="/analytics" class="btn btn-primary">查看分析</a>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">🤖 系统特性</h5>
                <div class="row">
                    <div class="col-md-6">
                        <h6>语义网技术</h6>
                        <ul>
                            <li><strong>RDF/RDFS</strong>: 结构化数据存储和查询</li>
                            <li><strong>SPARQL</strong>: 强大的图数据查询语言</li>
                            <li><strong>OWL</strong>: 本体建模和推理</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6>智能功能</h6>
                        <ul>
                            <li>🎯 个性化课程推荐</li>
                            <li>🔍 先修要求检查</li>
                            <li>📊 学习路径规划</li>
                            <li>📈 性能分析和建议</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

STUDENTS_TEMPLATE = '''
{% extends "base.html" %}

{% block title %}Students - Education Management System{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>👥 学生管理</h1>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5>学生列表</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>学号</th>
                                <th>姓名</th>
                                <th>GPA</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for student in students %}
                            <tr>
                                <td>{{ student.Student_ID }}</td>
                                <td>{{ student.Name }}</td>
                                <td>{{ "%.2f"|format(student.GPA) }}</td>
                                <td>
                                    <a href="/student/{{ student.Student }}" class="btn btn-sm btn-primary">详情</a>
                                    <a href="/recommendations/{{ student.Student }}" class="btn btn-sm btn-success">推荐</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

def create_project_structure():
    """创建完整的项目文件结构"""
    
    # 创建主要目录
    directories = [
        'templates',
        'static/css',
        'static/js',
        'data',
        'docs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
    
    # 创建HTML模板文件
    templates = {
        'templates/base.html': BASE_TEMPLATE,
        'templates/index.html': INDEX_TEMPLATE,
        'templates/students.html': STUDENTS_TEMPLATE
    }
    
    for filepath, content in templates.items():
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 创建模板: {filepath}")

if __name__ == "__main__":
    create_project_structure()
    print("🎉 项目结构创建完成！请根据需要添加更多文件和功能。")