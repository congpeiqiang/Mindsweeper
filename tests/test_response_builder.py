"""
ResponseBuilder 单元测试

测试所有响应构建方法的功能
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.schema.response import ResponseBuilder


def test_success_response():
    """测试成功响应 (200)"""
    response = ResponseBuilder.success(
        data={"id": 1, "name": "test"},
        message="操作成功"
    )
    
    assert response["code"] == 200
    assert response["message"] == "操作成功"
    assert response["data"] == {"id": 1, "name": "test"}
    assert "timestamp" in response
    print("✅ test_success_response 通过")


def test_created_response():
    """测试创建成功响应 (201)"""
    response = ResponseBuilder.created(
        data={"id": 1, "name": "new"},
        message="创建成功"
    )
    
    assert response["code"] == 201
    assert response["message"] == "创建成功"
    assert response["data"] == {"id": 1, "name": "new"}
    assert "timestamp" in response
    print("✅ test_created_response 通过")


def test_accepted_response():
    """测试接受响应 (202)"""
    response = ResponseBuilder.accepted(
        data={"task_id": "abc123"},
        message="任务已接受"
    )
    
    assert response["code"] == 202
    assert response["message"] == "任务已接受"
    assert response["data"] == {"task_id": "abc123"}
    assert "timestamp" in response
    print("✅ test_accepted_response 通过")


def test_no_content_response():
    """测试无内容响应 (204)"""
    response = ResponseBuilder.no_content(message="删除成功")
    
    assert response["code"] == 204
    assert response["message"] == "删除成功"
    assert response["data"] is None
    assert "timestamp" in response
    print("✅ test_no_content_response 通过")


def test_bad_request_response():
    """测试请求错误响应 (400)"""
    response = ResponseBuilder.bad_request(
        message="参数错误",
        data={"field": "email"}
    )
    
    assert response["code"] == 400
    assert response["message"] == "参数错误"
    assert response["data"] == {"field": "email"}
    assert "timestamp" in response
    print("✅ test_bad_request_response 通过")


def test_unauthorized_response():
    """测试未授权响应 (401)"""
    response = ResponseBuilder.unauthorized(message="认证失败")
    
    assert response["code"] == 401
    assert response["message"] == "认证失败"
    assert response["data"] is None
    assert "timestamp" in response
    print("✅ test_unauthorized_response 通过")


def test_forbidden_response():
    """测试禁止访问响应 (403)"""
    response = ResponseBuilder.forbidden(message="权限不足")
    
    assert response["code"] == 403
    assert response["message"] == "权限不足"
    assert response["data"] is None
    assert "timestamp" in response
    print("✅ test_forbidden_response 通过")


def test_not_found_response():
    """测试资源不存在响应 (404)"""
    response = ResponseBuilder.not_found(message="资源不存在")
    
    assert response["code"] == 404
    assert response["message"] == "资源不存在"
    assert response["data"] is None
    assert "timestamp" in response
    print("✅ test_not_found_response 通过")


def test_conflict_response():
    """测试冲突响应 (409)"""
    response = ResponseBuilder.conflict(
        message="资源已存在",
        data={"existing_id": "123"}
    )
    
    assert response["code"] == 409
    assert response["message"] == "资源已存在"
    assert response["data"] == {"existing_id": "123"}
    assert "timestamp" in response
    print("✅ test_conflict_response 通过")


def test_unprocessable_entity_response():
    """测试无法处理的实体响应 (422)"""
    response = ResponseBuilder.unprocessable_entity(
        message="验证失败",
        data={"errors": [{"field": "age", "message": "必须是正整数"}]}
    )
    
    assert response["code"] == 422
    assert response["message"] == "验证失败"
    assert "errors" in response["data"]
    assert "timestamp" in response
    print("✅ test_unprocessable_entity_response 通过")


def test_internal_error_response():
    """测试服务器错误响应 (500)"""
    response = ResponseBuilder.internal_error(
        message="服务器错误",
        data={"error_id": "err_123"}
    )
    
    assert response["code"] == 500
    assert response["message"] == "服务器错误"
    assert response["data"] == {"error_id": "err_123"}
    assert "timestamp" in response
    print("✅ test_internal_error_response 通过")


def test_service_unavailable_response():
    """测试服务不可用响应 (503)"""
    response = ResponseBuilder.service_unavailable(message="服务不可用")
    
    assert response["code"] == 503
    assert response["message"] == "服务不可用"
    assert response["data"] is None
    assert "timestamp" in response
    print("✅ test_service_unavailable_response 通过")


def test_response_structure():
    """测试响应结构完整性"""
    response = ResponseBuilder.success(data={"test": "data"})
    
    # 验证所有必需字段
    assert "code" in response
    assert "message" in response
    assert "data" in response
    assert "timestamp" in response
    
    # 验证字段类型
    assert isinstance(response["code"], int)
    assert isinstance(response["message"], str)
    assert isinstance(response["timestamp"], str)
    
    print("✅ test_response_structure 通过")


def test_timestamp_format():
    """测试时间戳格式"""
    response = ResponseBuilder.success()
    timestamp = response["timestamp"]
    
    # 验证时间戳格式 (ISO 8601)
    try:
        datetime.fromisoformat(timestamp)
        print("✅ test_timestamp_format 通过")
    except ValueError:
        raise AssertionError(f"时间戳格式不正确: {timestamp}")


def test_default_values():
    """测试默认值"""
    # 测试默认消息
    response = ResponseBuilder.success()
    assert response["message"] == "success"
    
    # 测试默认数据
    response = ResponseBuilder.not_found()
    assert response["data"] is None
    
    print("✅ test_default_values 通过")


if __name__ == "__main__":
    print("")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║           ResponseBuilder 单元测试                            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("")
    
    try:
        test_success_response()
        test_created_response()
        test_accepted_response()
        test_no_content_response()
        test_bad_request_response()
        test_unauthorized_response()
        test_forbidden_response()
        test_not_found_response()
        test_conflict_response()
        test_unprocessable_entity_response()
        test_internal_error_response()
        test_service_unavailable_response()
        test_response_structure()
        test_timestamp_format()
        test_default_values()
        
        print("")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                  ✅ 所有测试通过！                            ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print("")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

